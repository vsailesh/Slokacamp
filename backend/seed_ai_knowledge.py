"""Seed sample knowledge documents for AI Tutor"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slokcamp.settings')
django.setup()

from ai_tutor.models import KnowledgeDocument
from ai_tutor.rag_service import rag_service
from accounts.models import User

# Sample Sanskrit slokas and Ayurvedic content
sample_documents = [
    {
        'title': 'Bhagavad Gita - Chapter 2, Verse 47',
        'document_type': 'sloka',
        'content': '''कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।
मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥

Translation: You have a right to perform your prescribed duty, but you are not entitled to the fruits of action. Never consider yourself to be the cause of the results of your activities, and never be attached to not doing your duty.

Meaning: This verse teaches the principle of Karma Yoga - performing one's duty without attachment to results. It emphasizes action without expectation of reward.

Context: This is one of the most important verses in the Bhagavad Gita, spoken by Lord Krishna to Arjuna. It forms the foundation of Karma Yoga philosophy.
''',
        'metadata': {'source': 'Bhagavad Gita', 'chapter': 2, 'verse': 47, 'language': 'Sanskrit'}
    },
    {
        'title': 'Introduction to Three Doshas',
        'document_type': 'ayurveda',
        'content': '''The Three Doshas in Ayurveda

Vata (Air + Space): Governs movement, breathing, circulation. Characteristics include dry, light, cold, rough, subtle, mobile. When balanced: creativity, vitality. When imbalanced: anxiety, dry skin, constipation.

Pitta (Fire + Water): Governs digestion, metabolism, energy production. Characteristics include hot, sharp, light, liquid, spreading. When balanced: intelligence, courage, good digestion. When imbalanced: anger, inflammation, acidity.

Kapha (Earth + Water): Governs structure, lubrication, stability. Characteristics include heavy, slow, cold, oily, smooth, dense, soft, stable. When balanced: love, calmness, forgiveness. When imbalanced: weight gain, congestion, lethargy.

Every individual has a unique constitution (Prakriti) which is a combination of these three doshas. Understanding your dosha helps in maintaining health and treating diseases.
''',
        'metadata': {'category': 'Fundamental Concepts', 'difficulty': 'beginner'}
    },
    {
        'title': 'Yoga Sutras of Patanjali - Sutra 1.2',
        'document_type': 'sloka',
        'content': '''योगश्चित्तवृत्तिनिरोधः॥

Transliteration: Yogaś-citta-vṛtti-nirodhaḥ

Translation: Yoga is the cessation of the fluctuations of the mind.

Meaning: This sutra defines yoga as the practice of controlling and stilling the modifications of the mind. When the mind is calm and focused, one experiences true yoga.

Explanation: Citta = consciousness/mind-stuff, Vritti = fluctuations/modifications, Nirodha = cessation/control. This is the fundamental definition of yoga, emphasizing mental discipline over physical postures.
''',
        'metadata': {'source': 'Yoga Sutras', 'pada': 1, 'sutra': 2}
    },
    {
        'title': 'Ayurvedic Daily Routine (Dinacharya)',
        'document_type': 'ayurveda',
        'content': '''Dinacharya - Daily Routine for Health

Morning (Brahma Muhurta - before sunrise):
- Wake up between 4-6 AM
- Eliminate waste (bowel movement)
- Clean teeth and tongue (scraping tongue removes toxins)
- Oil pulling (swishing sesame or coconut oil)
- Drink warm water

Self-care practices:
- Abhyanga (self-massage with warm oil)
- Exercise or Yoga (30 minutes)
- Meditation (10-20 minutes)
- Bathing

Meal times:
- Breakfast: 7-8 AM (light, optional)
- Lunch: 12-1 PM (main meal when digestive fire is strongest)
- Dinner: 6-7 PM (light, at least 2 hours before sleep)

Evening:
- Light walk after dinner
- Relaxation or gentle activities
- Sleep: 9-10 PM

Following dinacharya aligns your body with natural rhythms, promoting health and preventing disease.
''',
        'metadata': {'category': 'Lifestyle', 'difficulty': 'beginner'}
    },
]

def seed_documents():
    print("Seeding knowledge documents...")
    
    # Get or create admin user
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        print("No admin user found, creating default admin...")
        admin_user = User.objects.create_superuser(
            email='admin@slokcamp.com',
            password='Admin@123',
            first_name='Admin',
            last_name='User'
        )
    
    for doc_data in sample_documents:
        # Check if document exists
        existing = KnowledgeDocument.objects.filter(title=doc_data['title']).first()
        if existing:
            print(f"Document '{doc_data['title']}' already exists, skipping...")
            continue
        
        # Create document
        document = KnowledgeDocument.objects.create(
            title=doc_data['title'],
            document_type=doc_data['document_type'],
            content=doc_data['content'],
            metadata=doc_data['metadata'],
            uploaded_by=admin_user,
            is_active=True
        )
        
        print(f"Created document: {document.title}")
        
        # Process document (generate embeddings)
        try:
            chunks_created = rag_service.process_document(document)
            print(f"  ✓ Processed {chunks_created} chunks with embeddings")
        except Exception as e:
            print(f"  ✗ Failed to process document: {e}")
    
    print("\nKnowledge base seeding complete!")
    print(f"Total documents: {KnowledgeDocument.objects.count()}")
    print(f"Total chunks: {KnowledgeDocument.objects.first().chunks.count() if KnowledgeDocument.objects.exists() else 0}")

if __name__ == '__main__':
    seed_documents()
