import boto3
import json
from datetime import datetime, timedelta
from django.conf import settings
from botocore.exceptions import ClientError
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import time

class S3SignedURLGenerator:
    """Generate signed URLs for S3 content with CloudFront support"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # CloudFront configuration
        self.cloudfront_domain = getattr(settings, 'CLOUDFRONT_DOMAIN', '')
        self.cloudfront_key_id = getattr(settings, 'CLOUDFRONT_KEY_ID', '')
        self.cloudfront_private_key_path = getattr(settings, 'CLOUDFRONT_PRIVATE_KEY_PATH', '')
    
    def generate_s3_signed_url(self, bucket_name, object_key, expiration_minutes=60):
        """
        Generate a signed URL for direct S3 access
        
        Args:
            bucket_name (str): S3 bucket name
            object_key (str): S3 object key
            expiration_minutes (int): URL expiration time in minutes
            
        Returns:
            str: Signed URL
        """
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_key},
                ExpiresIn=expiration_minutes * 60
            )
            return response
        except ClientError as e:
            print(f"Error generating S3 signed URL: {e}")
            return None
    
    def generate_cloudfront_signed_url(self, object_key, expiration_minutes=60):
        """
        Generate a signed URL for CloudFront distribution
        
        Args:
            object_key (str): Object key in S3
            expiration_minutes (int): URL expiration time in minutes
            
        Returns:
            str: Signed CloudFront URL
        """
        if not all([self.cloudfront_domain, self.cloudfront_key_id, self.cloudfront_private_key_path]):
            # Fall back to S3 direct access
            return self.generate_s3_signed_url(settings.AWS_STORAGE_BUCKET_NAME, object_key, expiration_minutes)
        
        try:
            # Calculate expiration timestamp
            expire_time = int(time.time()) + (expiration_minutes * 60)
            
            # Create the URL to be signed
            cloudfront_url = f"https://{self.cloudfront_domain}/{object_key}"
            
            # Create the policy
            policy = {
                "Statement": [
                    {
                        "Resource": cloudfront_url,
                        "Condition": {
                            "DateLessThan": {
                                "AWS:EpochTime": expire_time
                            }
                        }
                    }
                ]
            }
            
            policy_json = json.dumps(policy, separators=(',', ':'))
            policy_base64 = base64.b64encode(policy_json.encode()).decode()
            
            # Load the private key
            with open(self.cloudfront_private_key_path, 'rb') as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None
                )
            
            # Sign the policy
            signature = private_key.sign(
                policy_json.encode(),
                padding.PKCS1v15(),
                hashes.SHA1()
            )
            
            signature_base64 = base64.b64encode(signature).decode()
            
            # Make base64 URL-safe
            policy_base64 = policy_base64.replace('+', '-').replace('=', '_').replace('/', '~')
            signature_base64 = signature_base64.replace('+', '-').replace('=', '_').replace('/', '~')
            
            # Construct the signed URL
            signed_url = f"{cloudfront_url}?Policy={policy_base64}&Signature={signature_base64}&Key-Pair-Id={self.cloudfront_key_id}"
            
            return signed_url
            
        except Exception as e:
            print(f"Error generating CloudFront signed URL: {e}")
            # Fall back to S3 direct access
            return self.generate_s3_signed_url(settings.AWS_STORAGE_BUCKET_NAME, object_key, expiration_minutes)
    
    def generate_streaming_urls(self, video_object, expiration_minutes=60):
        """
        Generate signed URLs for HLS and DASH streaming
        
        Args:
            video_object: Video model instance
            expiration_minutes (int): URL expiration time in minutes
            
        Returns:
            dict: Dictionary containing signed streaming URLs
        """
        urls = {}
        
        if video_object.hls_url:
            # Extract the object key from the HLS URL
            hls_key = video_object.hls_url.split('/')[-1]
            urls['hls'] = self.generate_cloudfront_signed_url(
                f"hls/{video_object.id}/{hls_key}",
                expiration_minutes
            )
        
        if video_object.dash_url:
            # Extract the object key from the DASH URL
            dash_key = video_object.dash_url.split('/')[-1]
            urls['dash'] = self.generate_cloudfront_signed_url(
                f"dash/{video_object.id}/{dash_key}",
                expiration_minutes
            )
        
        # Generate signed URL for thumbnail
        if video_object.thumbnail_url:
            thumbnail_key = f"thumbnails/{video_object.id}/thumbnail.jpg"
            urls['thumbnail'] = self.generate_cloudfront_signed_url(
                thumbnail_key,
                expiration_minutes * 24  # Thumbnails can have longer expiration
            )
        
        return urls

class VdoCipherIntegration:
    """Integration with VdoCipher for DRM-protected video streaming"""
    
    def __init__(self):
        self.api_secret = settings.VDOCIPHER_API_SECRET
        self.base_url = 'https://dev.vdocipher.com/api'
    
    def upload_video(self, video_file_path, title, description=''):
        """
        Upload video to VdoCipher
        
        Args:
            video_file_path (str): Path to video file
            title (str): Video title
            description (str): Video description
            
        Returns:
            dict: Upload response containing video ID
        """
        import requests
        
        # Get upload URL
        headers = {
            'Authorization': f'Apisecret {self.api_secret}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'title': title,
            'description': description
        }
        
        response = requests.post(
            f'{self.base_url}/videos',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"VdoCipher upload failed: {response.text}")
    
    def generate_otp(self, video_id, user_id, expiration_minutes=60):
        """
        Generate OTP for video playback
        
        Args:
            video_id (str): VdoCipher video ID
            user_id (str): User identifier
            expiration_minutes (int): OTP expiration in minutes
            
        Returns:
            dict: OTP response
        """
        import requests
        
        headers = {
            'Authorization': f'Apisecret {self.api_secret}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'licenseRules': {
                'canPersist': False,
                'rentalDuration': expiration_minutes * 60
            },
            'userId': str(user_id)
        }
        
        response = requests.post(
            f'{self.base_url}/videos/{video_id}/otp',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"VdoCipher OTP generation failed: {response.text}")
    
    def get_video_details(self, video_id):
        """
        Get video details from VdoCipher
        
        Args:
            video_id (str): VdoCipher video ID
            
        Returns:
            dict: Video details
        """
        import requests
        
        headers = {
            'Authorization': f'Apisecret {self.api_secret}'
        }
        
        response = requests.get(
            f'{self.base_url}/videos/{video_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"VdoCipher get video failed: {response.text}")

# Usage example
"""
# Initialize the signed URL generator
url_generator = S3SignedURLGenerator()

# Generate signed URL for a video file
signed_url = url_generator.generate_cloudfront_signed_url(
    'videos/course-1/lesson-1.mp4',
    expiration_minutes=30
)

# Generate streaming URLs for a video
video = Video.objects.get(id='some-video-id')
streaming_urls = url_generator.generate_streaming_urls(video, 60)

# Initialize VdoCipher integration
vdocipher = VdoCipherIntegration()

# Generate OTP for video playback
otp_response = vdocipher.generate_otp(
    video_id='vdocipher-video-id',
    user_id='user-uuid',
    expiration_minutes=30
)
"""