# Product Requirements Document: Resilience Recovery App

## 1. Product Overview

### 1.1 Vision
The Resilience Recovery App is a comprehensive mental health support platform that combines AI-powered emotional guidance with practical micro-win tracking to help users build resilience through small, achievable victories.

### 1.2 Mission
To provide accessible, personalized mental health support through compassionate AI agents and evidence-based positive psychology techniques that help users develop emotional resilience and celebrate their progress.

### 1.3 Target Audience
- Primary: Adults (18-65) experiencing stress, anxiety, or seeking emotional wellness support
- Secondary: Individuals in recovery, therapy participants, wellness enthusiasts
- Use Cases: Daily emotional check-ins, crisis support, progress tracking, habit building

## 2. Core Features

### 2.1 AI-Powered Reframing System
**Purpose**: Transform negative thought patterns through compassionate perspective shifts

**Features**:
- Emotion-aware response generation using Claude Haiku
- Non-judgmental, validating language patterns
- Contextual reframing based on user history
- Shame-defusing and resilience-recognizing responses

**API Requirements**:
- `POST /api/v1/reframes/generate` - Generate compassionate reframe
- `GET /api/v1/reframes/` - List user reframes
- `POST /api/v1/reframes/{id}/save` - Save reframe for later

**Success Metrics**:
- User engagement rate with reframes (target: >70%)
- Mood improvement scores post-reframe (target: +2 points avg)
- Reframe save rate (target: >40%)

### 2.2 Micro-Win Suggestion Engine
**Purpose**: Generate personalized, achievable activities that build momentum and confidence

**Features**:
- AI-generated win suggestions using GPT-4o-mini
- Category-based filtering (Movement, Mindfulness, Connection, Self-care, Productivity)
- Mood-adaptive difficulty scaling
- Historical success pattern learning

**API Requirements**:
- `GET /api/v1/wins/suggest` - Get personalized win suggestions
- `POST /api/v1/wins/complete` - Mark win as completed
- `GET /api/v1/wins/` - List user's saved wins
- `POST /api/v1/wins/` - Create custom win

**Success Metrics**:
- Win completion rate (target: >60%)
- User return rate after win completion (target: >80%)
- Custom win creation rate (target: >25% of users)

### 2.3 Reflection & Journal System
**Purpose**: Provide structured emotional processing and self-awareness building

**Features**:
- Free-form reflection entry
- Mood intensity tracking (1-10 scale)
- AI analysis for win suggestion context
- Historical reflection search and review

**API Requirements**:
- `POST /api/v1/reflections/` - Create reflection
- `GET /api/v1/reflections/` - List user reflections
- `GET /api/v1/reflections/{id}` - Get specific reflection
- `PUT /api/v1/reflections/{id}` - Update reflection
- `DELETE /api/v1/reflections/{id}` - Delete reflection

**Success Metrics**:
- Daily reflection completion rate (target: >40%)
- Reflection length increase over time (engagement indicator)
- Correlation between reflection frequency and mood scores

### 2.4 Dynamic Chat Assistant
**Purpose**: Provide contextual, mood-aware conversational support

**Features**:
- Listen vs. Nudge mode determination using Claude Haiku
- Conversation flow management with Claude Sonnet
- Crisis detection and appropriate resource routing
- Personalized conversation patterns

**API Requirements**:
- `POST /api/v1/chat/start` - Start new chat session
- `POST /api/v1/chat/message` - Send message in session
- `GET /api/v1/chat/sessions` - List user chat sessions
- `GET /api/v1/chat/sessions/{id}` - Get session with messages

**Success Metrics**:
- Session completion rate (target: >75%)
- User satisfaction scores (target: >4.2/5)
- Crisis detection accuracy (target: >95%)

### 2.5 Progress & Streak Tracking
**Purpose**: Visualize progress and maintain motivation through achievement tracking

**Features**:
- Current streak calculation
- Longest streak records
- Weekly/monthly progress summaries
- Achievement badges and milestones

**API Requirements**:
- `GET /api/v1/streaks/current` - Get current streak data
- `GET /api/v1/streaks/history` - Get streak history
- `POST /api/v1/streaks/update` - Update streak (auto-called)

**Success Metrics**:
- Average streak length (target: >7 days)
- Streak reset recovery rate (target: >60% return within 3 days)
- Long-term user retention (target: >40% at 30 days)

## 3. WinComplete Screen Feature

### 3.1 Feature Overview
The WinComplete screen is a celebration and reinforcement interface that appears immediately after a user completes a micro-win. This feature transforms the simple act of marking a task complete into a meaningful moment of recognition and positive reinforcement.

**Core Purpose**: 
- Celebrate user achievements to reinforce positive behavior patterns
- Provide immediate feedback and validation for completed actions
- Create psychological anchoring moments that increase motivation for future wins
- Gather post-completion insights for personalized recommendations

### 3.2 User Experience

**Screen Flow**:
1. User taps "Mark Complete" on any win
2. Brief loading animation (0.5-1 second)
3. WinComplete screen appears with celebration elements
4. User views completion summary and optional feedback
5. User can share achievement or continue to next suggested win
6. Return to main win dashboard with updated streak/progress

**Visual Elements**:
- **Header**: Congratulatory message with user's name
- **Win Summary**: Title, category, and completion time
- **Celebration Animation**: Subtle confetti or achievement badge animation
- **Mood Check**: Optional post-completion mood rating (1-10 scale)
- **Reflection Prompt**: "How did this make you feel?" text input (optional)
- **Next Actions**: 
  - "Share Achievement" button
  - "Try Another Win" button with AI-suggested follow-up
  - "View Progress" button linking to streak dashboard

**Personalization Elements**:
- Time-based congratulations ("Great way to start your morning!")
- Streak-aware messaging ("That's 5 days in a row!")
- Category-specific encouragement ("Movement wins are your strength!")
- Historical context ("Your best week yet!")

### 3.3 API Requirements

The WinComplete screen requires two primary API endpoints that are already implemented:

**Primary Endpoints**:
```
GET /api/v1/wins/{id}
- Purpose: Retrieve detailed win information for completion screen
- Response: WinResponse with title, description, category, estimated_minutes
- Usage: Display win details and context on completion screen
```

```
GET /api/v1/wins/completions/{id}
- Purpose: Retrieve completion record with user notes and mood data
- Response: WinCompletionResponse with completion_id, notes, mood_after, completed_at
- Usage: Show completion timestamp, user notes, and mood tracking data
```

**Supporting Endpoints** (existing):
```
POST /api/v1/wins/complete
- Purpose: Create the completion record that triggers the WinComplete screen
- Payload: WinCompletionCreate with win_id, reflection_id, notes, mood_after
```

```
GET /api/v1/streaks/current
- Purpose: Fetch updated streak information for celebration messaging
- Usage: Display current streak count and achievement level
```

**Data Flow**:
1. User completes win → `POST /api/v1/wins/complete` creates completion record
2. WinComplete screen loads → `GET /api/v1/wins/{id}` fetches win details
3. Screen displays completion data → `GET /api/v1/wins/completions/{id}` gets completion record
4. Streak information updates → `GET /api/v1/streaks/current` shows progress
5. Optional follow-up actions → Various endpoints based on user choice

### 3.4 Psychological Benefits

**Positive Reinforcement Loop**:
- **Immediate Gratification**: Instant celebration creates dopamine release
- **Achievement Recognition**: Formal acknowledgment of progress builds self-efficacy
- **Progress Visualization**: Seeing streak/progress data reinforces commitment
- **Social Validation**: Sharing options create community support opportunities

**Behavioral Psychology Principles**:
- **Variable Ratio Reinforcement**: Different celebration messages prevent habituation
- **Implementation Intention**: "Try Another Win" prompts create action planning
- **Self-Monitoring**: Mood tracking increases self-awareness and engagement
- **Goal Gradient Effect**: Progress display motivates continued effort

**Therapeutic Value**:
- **Cognitive Restructuring**: Celebration reframes small actions as meaningful achievements
- **Mindfulness Practice**: Post-completion reflection promotes present-moment awareness
- **Behavioral Activation**: Success experience increases likelihood of future engagement
- **Self-Compassion**: Positive messaging counters self-critical thought patterns

### 3.5 Technical Implementation

**Frontend Architecture**:
```
WinCompleteScreen/
├── components/
│   ├── CelebrationHeader.tsx     # Congratulatory messaging
│   ├── WinSummaryCard.tsx        # Win details display
│   ├── MoodRatingWidget.tsx      # Post-completion mood check
│   ├── ReflectionInput.tsx       # Optional notes input
│   ├── NextActionButtons.tsx     # Share/Continue options
│   └── ProgressIndicator.tsx     # Streak/achievement display
├── hooks/
│   ├── useWinCompletion.ts       # API calls and state management
│   ├── useStreakData.ts          # Progress tracking
│   └── useCelebrationMessages.ts # Personalized messaging
└── utils/
    ├── celebrationAnimations.ts  # Animation configurations
    └── shareHelpers.ts          # Social sharing functionality
```

**Screen Navigation**:
```
WinDashboard → SelectWin → ConfirmCompletion → [API Call] → WinCompleteScreen
                                                              ↓
NextWin ← ShareScreen ← ProgressView ← [User Action Choice]
```

**Data Management**:
- **State Management**: React Context or Redux for completion data
- **Caching**: Cache win details and user progress for offline functionality
- **Optimistic Updates**: Show celebration immediately, sync in background
- **Error Handling**: Graceful fallbacks if API calls fail during celebration

**Performance Considerations**:
- **Lazy Loading**: Load celebration animations only when screen appears
- **Image Optimization**: Compress celebration graphics and icons
- **API Batching**: Combine win details and streak data in single request where possible
- **Background Sync**: Update progress data while user views celebration

### 3.6 Error Handling

**API Failure Scenarios**:
- **Win Details Not Found**: Show generic celebration with cached win title
- **Network Timeout**: Display offline celebration, sync when reconnected
- **Completion Record Missing**: Log error but still show celebration screen
- **Streak Data Unavailable**: Show completion without streak information

**User Experience Fallbacks**:
- **Animation Failures**: Fall back to static celebration screen
- **Sharing Failures**: Provide alternative ways to record achievement
- **Navigation Issues**: Always provide clear path back to main dashboard

**Error Recovery**:
- **Retry Logic**: Automatic retry for failed API calls with exponential backoff
- **User Notification**: Clear, non-alarming messages about temporary issues
- **Data Integrity**: Ensure completion is recorded even if celebration fails

### 3.7 Success Metrics

**Engagement Metrics**:
- **Screen Completion Rate**: % of users who view full WinComplete screen (target: >90%)
- **Time on Screen**: Average time spent viewing celebration (target: 15-30 seconds)
- **Interaction Rate**: % of users who interact with screen elements (target: >60%)
- **Return Engagement**: % of users who complete another win within 24 hours (target: >45%)

**Behavioral Impact Metrics**:
- **Win Completion Frequency**: Increase in average wins per user per week (target: +25%)
- **Streak Maintenance**: Improvement in average streak length (target: +30%)
- **User Retention**: 7-day and 30-day retention rates (target: 70% and 40% respectively)
- **Feature Usage**: Adoption rate of mood tracking and reflection features (target: >50%)

**Quality Metrics**:
- **Mood Improvement**: Average mood rating increase post-completion (target: +1.5 points)
- **User Satisfaction**: Rating of celebration experience (target: >4.5/5)
- **Share Rate**: % of completions that are shared (target: >20%)
- **Personalization Effectiveness**: Relevance rating of congratulatory messages (target: >4.0/5)

**Technical Performance Metrics**:
- **Screen Load Time**: Time from completion tap to celebration display (target: <2 seconds)
- **API Response Time**: Average response time for completion endpoints (target: <500ms)
- **Error Rate**: Failed celebrations due to technical issues (target: <2%)
- **Crash Rate**: App crashes during WinComplete flow (target: <0.1%)

## 4. Technical Architecture

### 4.1 Backend Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth with JWT tokens
- **AI Services**: Anthropic Claude (Haiku/Sonnet), OpenAI GPT-4o-mini
- **Deployment**: Containerized with Docker, hosted on Fly.io

### 4.2 API Design Principles
- **RESTful Architecture**: Consistent endpoint naming and HTTP methods
- **Version Control**: All endpoints under `/api/v1/` namespace
- **Error Handling**: Standardized error responses with proper HTTP status codes
- **Data Validation**: Pydantic models for request/response validation
- **Security**: JWT authentication, rate limiting, input sanitization

### 4.3 Data Models
- **User**: Authentication and profile data
- **Reflection**: Journal entries and mood tracking
- **Win**: Suggested and custom achievements
- **WinCompletion**: Completion records and feedback
- **Reframe**: AI-generated perspective shifts
- **ChatSession**: Conversation history and context
- **Streak**: Progress tracking and statistics

### 4.4 AI Agent Architecture
All AI services inherit from `BaseAgent` class providing:
- Standardized input/output interfaces
- Error handling and fallback responses
- Conversation context management
- Model switching capabilities
- Usage monitoring and cost tracking

## 5. Security & Privacy

### 5.1 Data Protection
- **Encryption**: All data encrypted at rest and in transit
- **Privacy**: No sharing of personal data with third parties
- **Anonymization**: AI training data anonymized and aggregated
- **Retention**: User data deletion upon account termination
- **Compliance**: GDPR and CCPA compliant data handling

### 5.2 Authentication & Authorization
- **Multi-factor Authentication**: Optional 2FA for enhanced security
- **Session Management**: Secure JWT token handling with refresh rotation
- **Role-based Access**: Admin, user, and service account permissions
- **API Security**: Rate limiting, request validation, and abuse prevention

## 6. Testing & Quality Assurance

### 6.1 Testing Strategy
- **Unit Tests**: 90%+ code coverage for all API endpoints
- **Integration Tests**: End-to-end API workflow testing
- **AI Service Tests**: Mock and real API testing for AI agents
- **Performance Tests**: Load testing for expected user volumes
- **Security Tests**: Vulnerability scanning and penetration testing

### 6.2 Quality Metrics
- **API Reliability**: 99.9% uptime target
- **Response Times**: <500ms for standard endpoints, <3s for AI endpoints
- **Error Rates**: <1% for API calls, <5% for AI services (with fallbacks)
- **User Satisfaction**: >4.5/5 average rating
- **Support Resolution**: <2 hour response time for critical issues

## 7. Launch & Rollout Strategy

### 7.1 Beta Testing Phase
- **Closed Beta**: 50-100 users for 4 weeks
- **Features**: Core functionality without advanced AI features
- **Goals**: Validate user workflows, identify critical bugs
- **Success Criteria**: >80% feature completion rate, <5% crash rate

### 7.2 Phased Feature Rollout
- **Phase 1**: Basic reflection and win tracking
- **Phase 2**: AI reframing and win suggestions
- **Phase 3**: Chat assistant and advanced analytics
- **Phase 4**: Social features and community elements

### 7.3 Success Metrics
- **User Acquisition**: 1,000 active users within 3 months
- **Engagement**: 60% weekly active user rate
- **Retention**: 40% 30-day retention rate
- **Revenue**: Sustainable user acquisition cost vs. lifetime value
- **Clinical Impact**: Measurable mood improvement in user surveys

## 8. Future Roadmap

### 8.1 Near-term Enhancements (3-6 months)
- **Advanced Analytics**: Personal insight dashboard
- **Customizable Themes**: Personalized app appearance
- **Offline Functionality**: Core features available without internet
- **Integration APIs**: Third-party wellness app connections

### 8.2 Long-term Vision (6-12 months)
- **Community Features**: Peer support and group challenges
- **Professional Tools**: Therapist dashboard and client management
- **Wearable Integration**: Fitness tracker and health data sync
- **Advanced AI**: Personalized intervention timing and content

### 8.3 Platform Expansion
- **Web Application**: Browser-based access for desktop users
- **API Platform**: Third-party developer access to resilience tools
- **Enterprise Version**: Workplace wellness and employee assistance programs
- **Research Partnerships**: Academic collaboration for effectiveness studies

---

*This PRD serves as the foundational document for the Resilience Recovery App development. It should be reviewed and updated quarterly based on user feedback, market research, and technical capabilities.*