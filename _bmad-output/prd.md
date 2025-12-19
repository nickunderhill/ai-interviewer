---
stepsCompleted: [1, 2, 3, 4, 6, 7, 8, 9, 10]
inputDocuments:
  - '_bmad-output/analysis/product-brief-ai-interviewer-2025-12-17.md'
documentCounts:
  briefs: 1
  research: 0
  brainstorming: 0
  projectDocs: 0
workflowType: 'prd'
lastStep: 10
project_name: 'ai-interviewer'
user_name: 'Nick'
date: '2025-12-17'
---

# Product Requirements Document - ai-interviewer

**Author:** Nick **Date:** 2025-12-17

## Executive Summary

**ai-interviewer** is an open-source web application that revolutionizes
interview preparation by providing AI-driven, context-aware practice sessions
tailored to both the target role and the candidate's background. Unlike generic
interview prep tools or freeform ChatGPT sessions, ai-interviewer adapts
questions dynamically based on dual context (job description + candidate
résumé), delivers structured feedback with actionable learning recommendations,
and enables measurable progress tracking through session retakes.

The platform addresses a critical gap for recent graduates and mid-career
switchers who need interview practice but lack access to knowledgeable peers or
affordable personalized coaching. By implementing a BYOK (Bring Your Own Key)
model, users supply their own OpenAI API credentials, eliminating subscription
fees and making the tool sustainably open-source and cost-transparent.

### What Makes This Special

**ai-interviewer** differentiates itself through four core innovations:

1. **Dual-Context Adaptation**: Interview questions are generated considering
   both the job requirements AND the candidate's specific experience, creating
   truly personalized practice scenarios rather than generic question lists.

2. **Structured Learning Feedback**: Beyond simple scores, the system analyzes
   answers across multiple dimensions (relevance, completeness, technical
   accuracy, clarity) and identifies specific knowledge gaps with targeted
   learning recommendations.

3. **Measurable Progress Tracking**: Session history with comparable metrics
   enables users to track improvement over time, building confidence through
   visible skill development rather than subjective feelings of readiness.

4. **Open & Sustainable Model**: BYOK architecture eliminates recurring platform
   fees, ensures cost transparency, and makes the tool accessible to anyone with
   an OpenAI account while maintaining a healthy open-source community
   contribution model.

**The magic moment** occurs when candidates see feedback that directly connects
their specific background to role requirements—realizing this isn't generic prep
but genuine skill assessment. The platform challenges the assumption that
interview preparation must be one-size-fits-all, proving that personalized,
iterative practice with measurable outcomes produces better-prepared candidates
who land roles matching their actual capabilities.

## Project Classification

**Technical Type:** Web Application (SPA with API Backend)  
**Domain:** EdTech (Educational Technology)  
**Complexity:** Medium  
**Project Context:** Greenfield - new project

**Technical Architecture:**

- **Frontend:** React (modern SPA)
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **AI Integration:** OpenAI API (user-provided keys)
- **Infrastructure:** Docker containerization, GitHub Actions CI/CD

**Domain Considerations:**

- Educational technology with focus on skill development and learning outcomes
- Privacy considerations for user résumés and interview session data
- Content quality assurance for AI-generated questions and feedback
- Potential future considerations: educational privacy standards (FERPA/COPPA if
  expanding to institutions)

## Success Criteria

### User Success

**ai-interviewer** achieves user success when candidates experience measurable
improvement in interview preparedness and confidence:

- **Actionable Insight Moment**: User completes an interview session and
  receives feedback revealing specific knowledge gaps they weren't aware of
  (e.g., "Your Python experience didn't address the senior-level distributed
  systems requirements in this JD")
- **Measurable Progress**: User retakes the same role type and sees score
  improvement of 20%+ with clearer, more complete answers in previously weak
  areas
- **Preparation Confidence**: User feels genuinely prepared (not just rehearsed)
  for real interviews because they've practiced with questions relevant to their
  specific target role and background
- **Real-World Validation**: Users attribute successful interview outcomes to
  preparation with ai-interviewer

**Success Validation**: Users realize this isn't generic advice when they see
feedback that directly connects their résumé details to job requirements with
specific learning recommendations.

### Business Success

As an open-source academic project with BYOK model, success is measured through
research validation and community adoption:

**Academic/Research Success** (Primary):

- **Scientific Validation**: Demonstrate that 70%+ of users show measurable
  improvement after 3 sessions, validating the dual-context adaptation approach
- **Publishable Results**: Data proving learning gap identification accuracy and
  progress tracking effectiveness compared to generic interview prep
- **Reproducibility**: Other researchers can deploy and validate the approach
  independently

**Open-Source Community Success**:

- **Adoption Indicator**: 50+ GitHub stars and 5+ actual deployments within 6
  months of release
- **Community Engagement**: Active issues, feature requests, and contributions
  indicating real-world usage
- **Validation Use Cases**: External users provide feedback validating the
  scientific approach

**Project Completion Success**:

- MVP deployed and functional within diploma timeline
- Core workflows validated: session creation → adaptive interview → structured
  feedback → progress tracking
- Documentation complete for self-hosting and research reproducibility

### Technical Success

**System Reliability**:

- 95%+ session completion rate without crashes or data loss
- OpenAI API failures handled gracefully with clear user feedback
- Database integrity maintained across all transactions (no lost sessions,
  answers, or feedback)

**Performance**:

- Question generation: < 10 seconds per question
- Answer analysis and feedback: < 30 seconds after submission
- UI responsiveness maintained during AI processing (loading states, no freezes)

**Security & Privacy**:

- User OpenAI API keys encrypted at rest
- Résumé data protected (not shared beyond user's OpenAI account)
- Session data isolated per user with authentication
- Basic auth prevents unauthorized access

**Maintainability & Reproducibility**:

- Clean code supporting future research iterations
- Docker Compose enables one-command local deployment
- CI/CD pipeline catches regressions (tests, linting)
- Documentation supports external validation

### Measurable Outcomes

**MVP Success Threshold**:

- 10 external users complete 3+ interview sessions each
- 70% of multi-session users show score improvement of 15%+ across retakes
- System maintains 95%+ uptime during validation period
- Zero critical security vulnerabilities or data breaches

**Scientific Contribution Validated When**:

- Data demonstrates dual-context (JD + résumé) produces better outcomes than
  single-context approaches
- Learning gap identification shows correlation with actual skill deficiencies
- Progress tracking metrics prove reliable across multiple user cohorts

## Product Scope

### MVP - Minimum Viable Product

**Core User Workflows** (Must Work):

1. **User Management**: Registration, login, minimal authentication
2. **Profile Setup**: Upload/paste résumé (text format), store candidate
   background
3. **Job Posting Management**: Create job posting with description, role, level,
   tech stack
4. **Interview Session**:
   - Create session from job posting + résumé
   - Generate adaptive questions using context-aware prompting (JD + résumé
     context)
   - Support question types: technical, behavioral, project experience
   - Text-based Q&A flow (no voice mode in MVP)
5. **Answer Analysis**:
   - Evaluate answers across criteria: job relevance, completeness, technical
     correctness, clarity/structure
   - Generate structured feedback per answer (what's good, what needs
     improvement)
   - Produce learning recommendations based on detected gaps
6. **History & Progress**:
   - Store full session history (questions, answers, scores, feedback,
     timestamps)
   - Enable retakes with same/updated job posting
   - Basic progress visualization (score trends, comparison across sessions)

**Technical Infrastructure**:

- FastAPI backend with core endpoints (jobs, résumés, sessions, analysis,
  history)
- PostgreSQL schema (users, job_postings, resumes, sessions, messages, scores)
- React frontend (SPA) for all user interactions
- OpenAI API integration with user-provided keys
- Docker Compose for local deployment (backend + DB + frontend)
- GitHub Actions: build, tests, lint

**MVP Exclusions** (Explicitly Out):

- Voice mode
- Mobile app
- Multi-language support
- Advanced analytics beyond basic trends
- Social/community features
- Job board integrations

### Growth Features (Post-MVP)

**Enhanced Analytics**:

- Skill gap evolution tracking over time
- "Interview readiness score" per role type
- Comparative benchmarking (anonymized)

**Richer Interview Experience**:

- Multiple question type frameworks (STAR method for behavioral, system design
  templates)
- Resume parsing into structured fields (vs. plain text only)
- Session templates for common roles (SWE, PM, Data Scientist)

**User Experience Improvements**:

- Export session reports (PDF summaries for review)
- Interview tips and best practices library
- Customizable evaluation criteria

**Community Features**:

- Share anonymized sessions as examples
- Community-contributed question banks
- Role-specific prep guides

### Vision (Future)

**Advanced Interaction**:

- Voice mode for realistic interview simulation
- Real-time interruptions and follow-up questions (like real interviewers)
- Video practice with body language feedback

**Broader Accessibility**:

- Multi-language support for international candidates
- Mobile apps (iOS/Android) for practice on-the-go
- Offline mode for question practice

**Ecosystem Integration**:

- Job board integration (auto-import JDs from LinkedIn, Indeed)
- Calendar integration for scheduled practice sessions
- Career coaching partnerships

**AI Enhancements**:

- Multiple LLM provider support (not just OpenAI)
- Fine-tuned models for industry-specific interviews
- Interviewer persona customization (friendly, tough, technical deep-dive)

## User Journeys

### Journey 1: Alex Chen - From Anxious Graduate to Confident Candidate

Alex just completed his Computer Science degree and has his first senior
software engineer interview with a startup in two weeks. He's terrified. His
friends are busy with their own job searches, and he doesn't know anyone working
at that level to practice with. Late one Sunday night, panicking about
behavioral questions, he discovers ai-interviewer on GitHub.

The next morning, Alex copies the job description from his email and pastes his
résumé into the system. Within seconds, the first question appears: "Tell me
about a time you optimized database performance in a production system." His
heart sinks—he's never worked on production systems. He types a hesitant answer
about a class project.

The feedback hits hard but fair: "Your answer focused on academic context, but
this senior role expects production-scale experience. Gap identified:
Understanding production database optimization, monitoring, and trade-offs.
Recommended learning: PostgreSQL query optimization, indexing strategies,
database profiling tools."

Alex spends the week learning those specific topics, then retakes the interview.
This time, he mentions what he's learned and how he'd approach it. His score
jumps from 4/10 to 7/10. More importantly, he understands exactly what he still
needs to work on. When the real interview comes, the interviewer asks about
system design—Alex references his learning journey and gets hired as a junior
engineer (not senior, but a foot in the door). He credits ai-interviewer for
helping him understand the gap between academic and industry expectations.

### Journey 2: Sarah Martinez - Career Switcher Finding Her Path

Sarah has been a project manager for five years but wants to transition into
product management at a tech company. She's applying to PM roles but keeps
getting rejected after first rounds. She doesn't know if it's her answers, her
background, or something else—no one gives her useful feedback.

A friend mentions ai-interviewer. Skeptical but desperate, Sarah creates an
account and uploads her PM-heavy résumé alongside a product manager job
description from her dream company. The first question: "How would you
prioritize features for our B2B SaaS dashboard given limited engineering
resources?"

She answers based on her project management experience, focusing on timelines
and stakeholder management. The feedback is eye-opening: "Your answer emphasized
execution over strategy. This PM role requires product strategy thinking: user
impact, business value, opportunity cost. Gap identified: Product prioritization
frameworks (RICE, value vs. effort), user research integration, strategic
trade-offs."

Sarah realizes she's been answering like a project manager, not a product
manager. Over three weeks, she retakes the interview five times, each time
incorporating strategic thinking frameworks. Her "product strategy" score goes
from 3/10 to 8/10. The feedback evolves from "too execution-focused" to "solid
strategic reasoning, connect more to user outcomes."

When she interviews at her target company two months later, she speaks their
language. She gets the offer. Looking back at her session history, Sarah can see
exactly when her thinking shifted from project management to product
strategy—the data proves her transformation.

### Journey 3: Marcus Johnson - The Retake That Changed Everything

Marcus bombed a technical interview at Google six months ago. He knew it went
badly but didn't know why—the recruiter's rejection email was generic: "We've
decided to move forward with other candidates."

He uses ai-interviewer to recreate that interview scenario: senior backend
engineer role, his exact résumé, similar questions to what he remembers. His
first score: 5.5/10. The detailed feedback shows three major gaps: system design
depth, distributed systems knowledge, and communication clarity. He's shocked—he
thought he knew backend engineering well.

Marcus spends four months learning: reading "Designing Data-Intensive
Applications," taking a distributed systems course, practicing explaining
technical concepts clearly. Every two weeks, he retakes the same interview
scenario. His progress chart becomes his motivator: 5.5 → 6.2 → 6.8 → 7.5 → 8.1
→ 8.7.

When he reapplies to Google nine months later, the interview feels completely
different. He's not guessing anymore—he knows the patterns, he can explain
trade-offs, he speaks with confidence. He gets the offer. His ai-interviewer
dashboard shows 12 sessions, 47 questions answered, and clear upward trends in
every category. That visual proof of improvement gave him the confidence to
reapply.

### Journey Requirements Summary

These three candidate journeys reveal the following core capabilities needed for
ai-interviewer:

**Session Management & Setup:**

- User registration and authentication
- Résumé upload/storage (text format initially)
- Job description creation and storage with role metadata (title, level, tech
  stack)
- Session creation linking job description + résumé

**Adaptive Interview Experience:**

- Question generation using dual context (job requirements + candidate
  background)
- Context-aware prompting that references both JD and résumé details
- Support for multiple question types (technical, behavioral, project
  experience)
- Text-based Q&A interface with clear question presentation

**Answer Evaluation & Feedback:**

- Multi-dimensional scoring across criteria:
  - Job relevance (does answer address role requirements?)
  - Completeness (thorough vs. superficial?)
  - Technical correctness (accurate understanding?)
  - Clarity/structure (well-communicated?)
- Structured feedback generation:
  - What's good (positive reinforcement)
  - What needs improvement (specific gaps)
  - Learning recommendations (actionable next steps with specific
    topics/resources)

**Progress Tracking & Retakes:**

- Full session history storage (questions, answers, scores, feedback,
  timestamps)
- Retake functionality for same job/résumé combination
- Score comparison across sessions (before/after visualization)
- Progress trends by evaluation criteria
- Visual dashboard showing improvement over time

**Emotional Journey Support:**

- Clear gap identification (anxiety → understanding)
- Actionable learning paths (confusion → direction)
- Measurable progress (doubt → confidence)
- Visual proof of improvement (motivation through data)

## Innovation & Novel Approaches

### Core Innovation: Dual-Context Adaptive Learning System

**ai-interviewer** introduces a novel approach to AI-powered interview
preparation by combining three innovation patterns that haven't been unified in
existing tools:

**1. Dual-Context Question Generation**

Traditional interview prep tools use either generic questions or
job-description-based questions. ai-interviewer is the first open-source tool to
synthesize BOTH job requirements AND candidate background simultaneously:

- **Innovation**: Questions reference specific résumé experiences in the context
  of job requirements (e.g., "Given your Python experience from Project X, how
  would you approach the distributed systems challenges mentioned in this senior
  backend role?")
- **Why It Matters**: Creates truly personalized practice that mirrors real
  interviews where interviewers evaluate fit between candidate and role
- **Market Gap**: Existing tools (PYTAI, MyPitch.guru, FoloUp) are either
  generic or job-focused, but don't integrate candidate context

**2. Closed-Loop Learning System**

Beyond simple Q&A, the system creates a measurable learning cycle:

```
Answer → Multi-dimensional Analysis → Gap Identification →
Specific Learning Recommendations → Retake → Score Improvement →
Progress Tracking → Confidence Building
```

- **Innovation**: Complete feedback loop with measurable progress validation
  (not just practice, but proven improvement)
- **Why It Matters**: Transforms interview prep from subjective "feeling ready"
  to objective "data shows 20% improvement"
- **Research Angle**: System generates its own validation data (users become
  research participants validating the approach)

**3. BYOK Sustainability Model**

Open-source AI tools typically fail due to API costs. ai-interviewer solves this
through user-supplied API keys:

- **Innovation**: Cost-transparent, infinitely scalable, community-sustainable
  AI education tool
- **Why It Matters**: Removes financial barriers to both users (no subscription)
  and maintainers (no infrastructure costs)
- **Ecosystem Impact**: Enables academic validation, community contributions,
  and reproducible research without commercial platform dependency

### Validation Approach

**Innovation Hypothesis**: Dual-context adaptation + structured learning loops
produce measurably better interview preparation outcomes than single-context or
generic approaches.

**Validation Methodology**:

1. **Quantitative**: Track score improvements across sessions (target: 70% show
   15%+ improvement by session 3)
2. **Qualitative**: User feedback on "magic moment" when they realize feedback
   is personalized
3. **Comparative**: Analyze single-context vs. dual-context question quality
   (blind evaluation)
4. **Academic**: Publish results demonstrating learning gap identification
   accuracy

**Success Metrics**:

- Users complete multiple sessions (validates engagement)
- Scores improve over time (validates learning effectiveness)
- Users report feeling more prepared (validates confidence building)
- External researchers replicate findings (validates reproducibility)

### Risk Mitigation & Fallbacks

**Risk 1: Dual-Context Quality**

- **Risk**: LLM might not effectively synthesize JD + résumé contexts
- **Mitigation**: Start with explicit prompt engineering; use few-shot examples;
  collect user feedback on question relevance
- **Fallback**: If dual-context quality is poor, fall back to JD-only mode until
  prompts improve

**Risk 2: Learning Gap Accuracy**

- **Risk**: AI-identified "gaps" might be inaccurate or misleading
- **Mitigation**: Multi-dimensional evaluation (not single score); transparent
  scoring criteria; user feedback on recommendation usefulness
- **Fallback**: Allow users to flag bad recommendations; adjust evaluation
  prompts based on feedback

**Risk 3: Progress Tracking Validity**

- **Risk**: Score improvements might not correlate with actual interview
  readiness
- **Mitigation**: User surveys on real interview outcomes; external validation
  studies; community feedback
- **Fallback**: Add disclaimers about score interpretation; focus on learning
  process over absolute scores

**Risk 4: BYOK Adoption Barrier**

- **Risk**: Users may not want to create OpenAI accounts or share API keys
- **Mitigation**: Clear documentation; cost transparency ($0.01-0.10 per session
  estimate); emphasize privacy/control
- **Fallback**: Consider hosted tier in future (post-MVP) if BYOK proves too
  complex for target users

### Market Context

**Existing Solutions & Gaps:**

- **ChatGPT/Generic AI**: No structured feedback, no progress tracking, no
  personalization to candidate background
- **PYTAI, MyPitch.guru**: Closed/paid services, no dual-context, limited open
  validation
- **FoloUp**: Recruiter-targeted, not candidate-focused, no learning loop

**ai-interviewer's Position**: First open-source, research-validated,
dual-context interview prep tool with measurable learning outcomes and
sustainable cost model.

## Web Application Specific Requirements

### Technical Architecture

**ai-interviewer** is implemented as a modern single-page application (SPA) with
API backend architecture optimized for MVP delivery and research validation.

**Frontend Architecture (React SPA):**

- Modern React with functional components and hooks
- Client-side routing (React Router)
- State management for session flow and progress tracking
- API client for backend communication
- Responsive design (desktop-first, mobile-compatible)

**Backend Architecture (FastAPI):**

- RESTful API endpoints for all operations
- OpenAI API integration for question generation and answer analysis
- PostgreSQL for persistent storage
- JWT authentication for session management
- Background task handling for long-running AI operations

### Browser & Platform Support

**MVP Browser Support:**

- **Target Browsers**: Chrome, Firefox, Safari, Edge (evergreen/latest versions
  only)
- **No Legacy Support**: IE11 and older browser versions explicitly not
  supported
- **Mobile Browsers**: Basic responsive support (works on tablets/phones,
  desktop is primary experience)
- **Viewport Strategy**: Desktop-first design (1024px+ optimal), responsive down
  to 768px, mobile functional but not optimized

**Rationale**: Focus MVP development on modern browser features; expand browser
support based on user analytics post-launch.

### Performance Requirements

**Loading & Responsiveness:**

- **Initial Page Load**: < 5 seconds on standard broadband connection
- **UI Interactions**: < 300ms response for navigation, button clicks, form
  submissions
- **API Response Times**:
  - Standard operations (save answer, load history): < 500ms
  - AI question generation: < 10 seconds (with progress indicator)
  - AI answer analysis: < 30 seconds (with progress indicator)

**User Experience During AI Processing:**

- Transparent loading states ("AI is generating your next question...")
- Progress indicators for long-running operations
- Non-blocking UI where possible (users can view previous Q&A while waiting)

**No Offline Support (MVP):**

- Application requires active internet connection
- All data persisted server-side in real-time
- Defer offline capabilities to post-MVP if user demand emerges

### Session Management & Persistence

**Session Continuity:**

- **Auto-save**: Questions and answers saved to database immediately upon
  submission
- **Resume Capability**: Users can close browser mid-interview and resume from
  last question
- **Session State**: All interview state (current question, history, scores)
  persisted in PostgreSQL
- **Timeout Policy**: Sessions remain accessible indefinitely; no
  auto-expiration for MVP

**Real-Time Communication:**

- **Polling Strategy**: Simple HTTP polling for AI operation status (no
  WebSocket complexity for MVP)
- **Frequency**: Poll every 2-3 seconds during AI processing
- **Fallback**: If operation exceeds expected time, display extended wait
  message with option to cancel

### SEO & Discoverability

**Minimal SEO for MVP:**

- **Public Landing Page**: Simple marketing page explaining the project, links
  to GitHub, login/signup
- **Behind-Login Content**: Interview sessions, history, progress dashboards not
  indexed
- **Open Graph Tags**: Proper OG tags for GitHub/social sharing (project looks
  professional when shared)
- **Robots.txt**: Allow indexing of landing page, disallow app routes

**No Complex SEO Optimization:**

- Not a content site; discoverability through GitHub, academic publications,
  word-of-mouth
- Defer SEO investment until post-MVP if organic search becomes acquisition
  channel

### Accessibility

**Basic WCAG Compliance (MVP):**

- **Semantic HTML**: Proper heading hierarchy, landmark regions, form labels
- **Keyboard Navigation**: All interactive elements accessible via keyboard
  (Tab, Enter, Esc)
- **Focus States**: Visible focus indicators for keyboard users
- **Alt Text**: Descriptive alt text for any images/icons
- **Color Contrast**: Minimum 4.5:1 contrast ratio for text

**Screen Reader Friendly:**

- ARIA labels for dynamic content updates ("New question loaded", "Feedback
  received")
- Text-based Q&A interface is inherently accessible (no complex visual
  interactions)
- Error messages and form validation communicated to assistive technologies

**Deferred to Post-MVP:**

- Formal WCAG AA validation and audit
- Comprehensive assistive technology testing
- Internationalization and multi-language support

**Rationale**: Text-based interface and semantic structure provide good baseline
accessibility; formalize validation once core functionality proven.

### Security & Privacy (Web-Specific)

**Client-Side Security:**

- HTTPS only (no HTTP access)
- Secure cookie handling for authentication tokens
- XSS protection through React's default escaping
- CSRF tokens for state-changing operations

**API Key Storage:**

- User OpenAI API keys encrypted at rest in PostgreSQL
- Never transmitted to client (server-side only usage)
- API proxy pattern (frontend never directly calls OpenAI)

**Data Privacy:**

- Session data isolated per user (no cross-user data leakage)
- Résumé content never shared beyond user's OpenAI account
- No third-party analytics or tracking in MVP (privacy-first approach)

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**Approach:** Problem-Solving + Academic Validation MVP

**ai-interviewer** MVP is designed to validate the core scientific hypothesis
(dual-context adaptation produces measurable learning outcomes) while delivering
genuine user value to early adopters. The scope balances research validation
requirements with practical implementation constraints of a diploma project
timeline.

**Strategic Rationale:**

- **Lean Core**: Focus exclusively on features that validate the innovation
  (dual-context + learning loop + progress tracking)
- **Research-First**: MVP generates data needed for academic publication and
  reproducibility validation
- **Sustainable Launch**: BYOK model eliminates operational costs, allowing
  focus on development over infrastructure
- **Iterative Validation**: Progress tracking built into MVP enables continuous
  validation of learning effectiveness

**MVP Success Criteria:**

- 10 external users complete 3+ sessions (validates engagement)
- 70% show 15%+ improvement (validates learning effectiveness)
- System runs reliably for validation period (validates technical approach)
- Publishable data demonstrates dual-context superiority (validates scientific
  contribution)

**Timeline Constraint:** Diploma completion timeline (~3-6 months from PRD to
validated MVP)

**Team Profile:** Solo developer (Nick) with academic research context,
intermediate skill level

### MVP Feature Set (Phase 1)

**Core User Journeys Supported:**

1. **New User Onboarding** → Register, configure API key, create profile with
   résumé
2. **First Interview Session** → Upload job description, receive personalized
   questions, submit answers, review feedback
3. **Progress Tracking** → View session history, compare scores, identify
   improvement areas
4. **Interview Retake** → Repeat same role/JD combination, measure improvement

**Must-Have Capabilities:**

**User Management:**

- Registration and login (minimal auth)
- User profile storage
- OpenAI API key configuration (encrypted storage)

**Content Management:**

- Résumé upload/paste (text format)
- Job posting creation (description, role, level, tech stack)
- Multi-posting support (users can practice for different roles)

**Interview Session Engine:**

- Session creation from JD + résumé pair
- Dual-context question generation (context-aware prompting with both inputs)
- Question type support: technical, behavioral, project experience
- Text-based Q&A interface
- Answer submission and storage

**AI Analysis & Feedback:**

- Multi-dimensional scoring (job relevance, completeness, technical accuracy,
  clarity)
- Structured feedback per answer (strengths, gaps, recommendations)
- Learning recommendations with specific topics/resources
- All analysis results persisted with session

**History & Progress:**

- Full session history (questions, answers, scores, feedback, timestamps)
- Session comparison (before/after views)
- Basic progress visualization (score trends by criteria)
- Retake functionality (same JD/résumé, new session ID)

**Technical Infrastructure:**

- FastAPI backend (REST API)
- React frontend (SPA)
- PostgreSQL database
- Docker Compose deployment
- GitHub Actions (build, test, lint)

**Explicit MVP Exclusions:**

- ❌ Voice mode (text-only for MVP)
- ❌ Mobile apps (web responsive covers basic mobile)
- ❌ Multi-language support (English only)
- ❌ Advanced analytics (beyond basic trends)
- ❌ Social/community features
- ❌ Job board integrations
- ❌ Multiple AI providers (OpenAI only)

### Post-MVP Features

**Phase 2: Growth & Enhancement (Post-Diploma)**

**Enhanced Analytics:**

- Skill gap evolution tracking over time
- "Interview readiness score" algorithm per role type
- Comparative benchmarking (anonymized user cohorts)
- Detailed breakdown by question type

**Richer Interview Experience:**

- STAR method framework for behavioral questions
- System design templates for technical roles
- Résumé parsing into structured fields
- Session templates for common roles (SWE, PM, Data Scientist)

**User Experience:**

- Export session reports (PDF summaries)
- Interview tips library
- Customizable evaluation criteria
- Mobile-optimized UI

**Phase 3: Expansion & Platform (Future Vision)**

**Advanced Interaction:**

- Voice mode for realistic simulation
- Real-time interruptions and follow-ups
- Video practice with body language feedback

**Broader Accessibility:**

- Multi-language support for international candidates
- Native mobile apps (iOS/Android)
- Offline mode for practice without connectivity

**Ecosystem:**

- Job board integrations (LinkedIn, Indeed auto-import)
- Calendar integration for scheduled practice
- Career coaching partnerships

**AI Enhancements:**

- Multiple LLM provider support (Anthropic, Gemini, local models)
- Fine-tuned models for industry-specific interviews
- Interviewer persona customization (friendly, tough, Socratic)

**Community:**

- Share anonymized sessions as examples
- Community-contributed question banks
- Role-specific prep guides

### Risk Mitigation Strategy

**Technical Risks:**

**Risk: Dual-context quality insufficient**

- **Mitigation**: Explicit prompt engineering with few-shot examples; user
  feedback collection on question relevance
- **Fallback**: JD-only mode if dual-context quality poor; iterate on prompts
  based on feedback
- **Validation**: Track question relevance scores in user feedback; target 80%+
  "relevant to my background" rating

**Risk: OpenAI API reliability/cost**

- **Mitigation**: BYOK model shifts cost to users; implement retry logic and
  graceful error handling
- **Fallback**: Clear user communication on API costs ($0.01-0.10 per session
  estimate); queue system if rate limits hit
- **Validation**: Monitor API failure rates; maintain 95%+ success rate

**Risk: Session state/data loss**

- **Mitigation**: Auto-save all Q&A to database immediately; PostgreSQL
  transaction integrity
- **Fallback**: Atomic operations; rollback on failure; session resume
  capability
- **Validation**: Zero data loss in user testing; database integrity checks

**Market Risks:**

**Risk: BYOK adoption barrier**

- **Mitigation**: Clear documentation; setup wizard; cost transparency; privacy
  emphasis
- **Fallback**: Consider hosted tier post-MVP if adoption blocked
- **Validation**: Track signup completion rate; target 70%+ who start signup
  complete API key configuration

**Risk: Insufficient user engagement (don't complete 3 sessions)**

- **Mitigation**: Progress visualization motivates retakes; email reminders
  (opt-in); clear value prop in first session
- **Fallback**: User interviews to understand drop-off; iterate on feedback
  quality
- **Validation**: Track session completion rates; identify drop-off points

**Risk: Learning improvement not measurable**

- **Mitigation**: Multi-dimensional scoring (not single number); longitudinal
  tracking; external validation studies
- **Fallback**: Focus on qualitative feedback if quantitative scores noisy
- **Validation**: Correlation analysis between scores and user-reported
  readiness

**Resource Risks:**

**Risk: Timeline overrun (diploma deadline)**

- **Mitigation**: Prioritize core innovation validation; defer polish and edge
  cases
- **Fallback**: Further scope reduction if needed—remove question type variety,
  simplify UI
- **Contingency**: Minimum deployable product = JD+résumé input → questions →
  feedback → basic history

**Risk: Technical complexity underestimated**

- **Mitigation**: Use proven tech stack (React, FastAPI, PostgreSQL); avoid
  novel frameworks
- **Fallback**: Simplify architecture—remove background task complexity,
  synchronous API calls only
- **Contingency**: Prototype critical path (dual-context prompting) early to
  validate feasibility

**Risk: Research validation insufficient**

- **Mitigation**: Built-in data collection from day 1; external user recruitment
  plan; reproducibility documentation
- **Fallback**: Self-validation with smaller sample size; focus on methodology
  over statistical significance
- **Contingency**: Case study approach (3-5 detailed user journeys) if
  quantitative validation weak

## Functional Requirements

### User Account Management

- **FR1**: Users can register for an account with email and password
- **FR2**: Users can log in to access their account
- **FR3**: Users can log out of their account
- **FR4**: Users can configure and store their OpenAI API key securely
- **FR5**: Users can view their profile information
- **FR6**: Users can update their stored OpenAI API key

### Résumé Management

- **FR7**: Users can upload a résumé in text format
- **FR8**: Users can paste résumé content directly into the system
- **FR9**: Users can view their stored résumé
- **FR10**: Users can edit their stored résumé
- **FR11**: Users can delete their résumé
- **FR12**: System stores résumé content associated with user account

### Job Posting Management

- **FR13**: Users can create a new job posting with description, role title,
  experience level, and tech stack
- **FR14**: Users can view all their saved job postings
- **FR15**: Users can edit existing job postings
- **FR16**: Users can delete job postings
- **FR17**: Users can select a job posting to start a new interview session
- **FR18**: System stores multiple job postings per user

### Interview Session Management

- **FR19**: Users can create a new interview session by selecting a job posting
  and using their stored résumé
- **FR20**: Users can view all their interview sessions (active and completed)
- **FR21**: Users can resume an incomplete interview session
- **FR22**: Users can view session details (job posting used, date created,
  status)
- **FR23**: System tracks session state (current question number, answered
  questions, pending questions)
- **FR24**: System persists session state to allow resumption after browser
  close

### Adaptive Question Generation

- **FR25**: System generates interview questions based on both job description
  and candidate résumé (dual-context)
- **FR26**: System generates questions across multiple types: technical,
  behavioral, and project experience
- **FR27**: System presents one question at a time to the user
- **FR28**: System tracks which questions have been answered in each session
- **FR29**: System generates follow-up questions that adapt based on previous
  answers
- **FR30**: Users can view the current question text
- **FR31**: Users can view question type (technical/behavioral/project)

### Answer Submission & Storage

- **FR32**: Users can type and submit text-based answers to questions
- **FR33**: Users can edit their answer before final submission
- **FR34**: System saves each answer with timestamp immediately upon submission
- **FR35**: Users can view their previously submitted answers in the current
  session
- **FR36**: System associates each answer with its corresponding question and
  session

### Answer Analysis & Feedback

- **FR37**: System analyzes each answer across multiple dimensions: job
  relevance, completeness, technical correctness, and clarity/structure
- **FR38**: System generates a numerical score for each evaluation dimension
- **FR39**: System generates structured feedback identifying answer strengths
- **FR40**: System generates structured feedback identifying areas for
  improvement
- **FR41**: System identifies specific knowledge gaps based on answer analysis
- **FR42**: System generates actionable learning recommendations with specific
  topics and resources
- **FR43**: Users can view complete feedback for each answered question
- **FR44**: System stores all scores and feedback with each answer

### Session History & Progress Tracking

- **FR45**: Users can view a list of all their completed interview sessions
- **FR46**: Users can view details of any past session (questions, answers,
  scores, feedback)
- **FR47**: Users can compare scores across multiple sessions for the same job
  posting
- **FR48**: System displays score trends over time by evaluation criteria
- **FR49**: System visualizes progress improvement across retakes
- **FR50**: Users can filter session history by job posting or date range
- **FR51**: Users can view aggregate statistics (total sessions, average scores,
  improvement trends)

### Interview Retake & Improvement Tracking

- **FR52**: Users can create a new session for the same job posting to retake an
  interview
- **FR53**: System tracks retake number for each job posting (attempt 1, 2, 3,
  etc.)
- **FR54**: System enables comparison of scores between original and retake
  sessions
- **FR55**: Users can view their improvement trajectory across multiple retakes
- **FR56**: System highlights which evaluation dimensions improved vs. declined
  in retakes

### AI Integration & Processing

- **FR57**: System uses user-provided OpenAI API keys to make API calls
- **FR58**: System handles OpenAI API errors gracefully and informs users
- **FR59**: System displays processing status during question generation (e.g.,
  "AI is generating your question...")
- **FR60**: System displays processing status during answer analysis (e.g.,
  "Analyzing your response...")
- **FR61**: System implements retry logic for transient API failures
- **FR62**: System never exposes user API keys to the frontend

### Data Privacy & Isolation

- **FR63**: System ensures each user can only access their own data (sessions,
  résumés, job postings)
- **FR64**: System encrypts stored OpenAI API keys at rest
- **FR65**: System does not share résumé content with any third parties beyond
  user's OpenAI account
- **FR66**: System isolates session data per user with no cross-user visibility

## Non-Functional Requirements

### Performance

**NFR-P1: Response Times**

- Standard UI interactions (navigation, button clicks, form submissions) must
  complete within 300ms
- Page initial load must complete within 5 seconds on standard broadband
  connection
- API operations for data retrieval (load history, fetch session) must complete
  within 500ms

**NFR-P2: AI Processing**

- Question generation must complete within 10 seconds with progress indication
- Answer analysis and feedback generation must complete within 30 seconds with
  progress indication
- System displays transparent loading states during all AI operations

**NFR-P3: UI Responsiveness**

- UI remains responsive during background AI processing (non-blocking
  operations)
- Users can view previous Q&A while waiting for new questions or feedback
- Polling for AI operation status occurs every 2-3 seconds without impacting UI
  performance

### Security

**NFR-S1: Authentication & Authorization**

- All user access requires authentication (no anonymous access to sessions or
  data)
- Session data isolated per user (no cross-user data visibility)
- JWT-based authentication with secure token storage

**NFR-S2: Data Encryption**

- OpenAI API keys encrypted at rest using industry-standard encryption (AES-256
  or equivalent)
- All data transmission occurs over HTTPS only (no HTTP access)
- Sensitive data (passwords, API keys) never logged in plain text

**NFR-S3: API Key Protection**

- User API keys never exposed to frontend/client
- API proxy pattern: backend acts as intermediary for all OpenAI calls
- API keys stored separately from other user data with restricted access

**NFR-S4: Data Privacy**

- Résumé content not shared with third parties beyond user's OpenAI account
- No tracking or analytics that compromise user privacy in MVP
- Session data remains private to individual users

**NFR-S5: Security Best Practices**

- XSS protection through React's default escaping mechanisms
- CSRF tokens for all state-changing operations
- Secure cookie handling with HttpOnly and Secure flags
- Input validation and sanitization on all user-submitted data

### Reliability

**NFR-R1: System Availability**

- System maintains 95%+ uptime during validation period
- Graceful degradation when OpenAI API unavailable (clear error messages, retry
  guidance)
- Database operations use transactions to maintain data integrity

**NFR-R2: Data Integrity**

- Zero data loss for submitted answers and generated feedback
- All Q&A saved to database immediately upon submission (auto-save)
- Atomic operations with rollback capability on failure
- Session state persistence enables resumption after browser close

**NFR-R3: Error Handling**

- OpenAI API failures handled gracefully with user-friendly error messages
- Retry logic implemented for transient API failures (3 retries with exponential
  backoff)
- System degrades gracefully rather than crashing on unexpected errors
- Users informed of errors with actionable next steps

**NFR-R4: Session Recovery**

- Users can resume incomplete sessions after browser close or connection loss
- No loss of progress within a session due to network interruptions
- Session state synchronized to database in real-time

### Maintainability & Reproducibility

**NFR-M1: Code Quality**

- Clean, documented code supporting future research iterations
- Modular architecture enabling component replacement or enhancement
- Consistent coding standards across frontend and backend

**NFR-M2: Deployment**

- One-command local deployment via Docker Compose
- Environment-based configuration (dev, staging, production)
- Automated database migrations for schema changes

**NFR-M3: Testing & CI/CD**

- Automated test suite covering critical paths (auth, session creation, Q&A
  flow)
- GitHub Actions workflow runs tests and linting on every commit
- Build failures prevent deployment to prevent regressions

**NFR-M4: Documentation**

- Complete setup documentation for external validation
- API documentation for reproducibility
- Architecture documentation for future contributors
- User documentation for BYOK setup and basic usage

**NFR-M5: Observability**

- Basic logging for debugging and troubleshooting
- API failure rate monitoring
- Session completion rate tracking for validation metrics

### Accessibility

**NFR-A1: Basic WCAG Compliance**

- Semantic HTML structure with proper heading hierarchy
- All interactive elements accessible via keyboard (Tab, Enter, Esc navigation)
- Visible focus indicators for keyboard users
- Minimum 4.5:1 color contrast ratio for text

**NFR-A2: Screen Reader Support**

- ARIA labels for dynamic content ("New question loaded", "Feedback received")
- Form labels properly associated with inputs
- Error messages communicated to assistive technologies
- Text-based Q&A interface inherently accessible (no complex visual interactions
  required)

**NFR-A3: Responsive Design**

- Desktop-first design (1024px+ optimal experience)
- Responsive down to 768px viewport (tablet support)
- Mobile viewports (< 768px) functional but not optimized (deferred to post-MVP)

### Browser Compatibility

**NFR-B1: Supported Browsers**

- Chrome, Firefox, Safari, Edge (evergreen/latest versions only)
- Modern JavaScript features (ES6+, async/await) without legacy polyfills
- No support for IE11 or older browsers

**NFR-B2: Progressive Enhancement**

- Core functionality works without JavaScript disabled warning displayed
- Graceful fallbacks for unsupported features
- Basic responsive behavior without complex media queries

### Scalability (MVP Constraints)

**NFR-SC1: MVP Capacity**

- System supports 10-50 concurrent users without performance degradation
- Database handles up to 1000 total sessions without optimization required
- OpenAI API rate limit handling (user-specific limits via BYOK model)

**NFR-SC2: Growth Readiness**

- Architecture supports horizontal scaling post-MVP if needed
- Database schema supports efficient querying at 10x scale
- No hard-coded limits that would require refactoring for growth
