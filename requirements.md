# Empty Classroom Finder - IIPS DAVV, Indore

## Original Problem Statement
A university web app for IIPS DAVV, Indore that interprets natural language queries from students and faculty to return actionable classroom availability results in JSON format.

### Key Requirements
- Campus hours: 8:00 AM - 6:30 PM only
- Filters: Floor (Ground, First, Second), Room ID, Capacity (30/60/120 seats), Facilities
- Room Data: LT-1 to LT-4, LH-2, LH-3, 101-109, 201-212 across 3 floors
- Facilities: Projector, Speaker, Whiteboard, Blackboard, Podium
- Predicted availability for next 30/60/90 minutes

## User Choices
- **AI Integration**: Gemini 3 Flash for natural language processing
- **Data**: Mock timetable data with realistic occupied/free periods
- **Authentication**: JWT-based user login (student/faculty roles)
- **Design**: Dark "Cyber-Academic" theme

## Architecture Completed

### Backend (FastAPI + MongoDB)
- `/api/auth/register` - User registration
- `/api/auth/login` - User authentication with JWT
- `/api/auth/me` - Get current user
- `/api/classrooms` - List all classrooms with status
- `/api/classrooms/{id}` - Get specific classroom
- `/api/search` - Natural language search powered by Gemini 3 Flash

### Frontend (React + Tailwind CSS)
- **LoginPage**: Email/password authentication
- **RegisterPage**: New user registration with role selection
- **DashboardPage**: Main search interface with room cards
- **AuthContext**: JWT token management

### Key Features Implemented
- Natural language search (e.g., "rooms on ground floor with projector")
- Floor-based filtering (Ground, First, Second)
- Real-time room status (Available/Occupied)
- Predicted availability (30m, 60m, 90m forecasts)
- Campus hours validation (8 AM - 6:30 PM)
- Responsive dark theme UI

## Next Tasks / Enhancements
1. **Real Timetable Integration**: Connect to actual IIPS DAVV class schedule API
2. **Room Booking**: Allow students/faculty to reserve available rooms
3. **Favorites**: Save frequently used rooms for quick access
4. **Notifications**: Alert when a favorite room becomes available
5. **Admin Panel**: Manage schedules and room configurations
6. **Mobile App**: Native iOS/Android app for on-the-go searches

## Tech Stack
- Backend: FastAPI, MongoDB, JWT Auth, Emergent Integrations (Gemini 3 Flash)
- Frontend: React, Tailwind CSS, Framer Motion, Shadcn UI
- Database: MongoDB (users collection)
