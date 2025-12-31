# 🚀 SlokaCamp Quick Start Guide

## Accessing the Applications

### 1. Web Application
**URL**: https://ayurlearn.preview.emergentagent.com

**Login**:
- Email: `admin@slokcamp.com`
- Password: `Admin@123`

**Features**:
- Browse courses
- User dashboard with progress
- Admin panel for user management
- Course enrollment

### 2. Django Admin Panel
**URL**: https://ayurlearn.preview.emergentagent.com/admin/

**Login**:
- Username: `admin@slokcamp.com`
- Password: `Admin@123`

**What you can do**:
- Manage users
- Create/Edit courses
- Add lessons to courses
- View enrollments
- Moderate reviews

### 3. API Documentation
**URL**: https://ayurlearn.preview.emergentagent.com/api/docs/

Interactive Swagger documentation for all API endpoints.

### 4. Mobile App
**Setup**:
```bash
cd /app/mobile-app
yarn start
```

**On your phone**:
1. Install Expo Go from App Store/Play Store
2. Scan QR code from terminal
3. Login with same credentials

---

## Testing the System

### Test User Registration:
1. Go to https://ayurlearn.preview.emergentagent.com/signup
2. Create a new account
3. Check Dashboard for sample courses

### Test Course Enrollment:
1. Browse courses at `/courses`
2. Click on a course
3. Enroll in the course
4. Check your dashboard for progress

### Test Admin Features:
1. Login as admin
2. Visit `/admin` page
3. View all users in admin panel
4. Access Django admin for full control

---

## API Testing Examples

### Get Access Token:
```bash
curl -X POST https://ayurlearn.preview.emergentagent.com/api/auth/signin/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@slokcamp.com","password":"Admin@123"}'
```

### Get Current User:
```bash
curl https://ayurlearn.preview.emergentagent.com/api/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### List Courses:
```bash
curl https://ayurlearn.preview.emergentagent.com/api/courses/
```

### Enroll in Course:
```bash
curl -X POST https://ayurlearn.preview.emergentagent.com/api/courses/enroll/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"course_id":"COURSE_UUID"}'
```

---

## Sample Data

### Users:
1. **Admin**: admin@slokcamp.com / Admin@123
2. **Test User**: test@example.com / Test@123

### Courses Available:
1. Introduction to Sanskrit Slokas (Beginner)
2. Ayurvedic Fundamentals (Beginner)
3. Meditation Mastery (Beginner)
4. Yoga Philosophy Deep Dive (Intermediate)

Each course has 12 lessons with video/audio/practice content.

---

## Mobile App Screenshots

The mobile app includes:
- 📱 Beautiful signin/signup screens
- 📊 Dashboard with XP and streak tracking
- 📚 Course catalog with search
- 🎯 Course details with enrollment
- 📈 Progress tracking

---

## Troubleshooting

### Backend not responding?
```bash
sudo supervisorctl restart backend
```

### Frontend not loading?
```bash
sudo supervisorctl restart frontend
```

### Check logs:
```bash
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.err.log
```

---

## Need Help?

- Check `/app/MIGRATION_COMPLETE.md` for full documentation
- API docs: https://ayurlearn.preview.emergentagent.com/api/docs/
- Django admin: https://ayurlearn.preview.emergentagent.com/admin/
