# Surveys App - Mixed Anonymity Model

A comprehensive Django app for creating and managing company surveys with a sophisticated mixed anonymity model designed to encourage honest feedback while maintaining appropriate levels of accountability.

## Features

### 🎯 **Mixed Anonymity Model**
- **ANONYMOUS**: Completely anonymous responses, no user tracking
- **ESCROW**: Private responses with optional follow-up opt-in
- **SIGNED**: Attributed responses for accountability and commitment

### 📊 **Survey Management**
- Create surveys with multiple sections and question types
- Drag-and-drop ordering with HTMX integration
- Flexible question types: Likert, NPS, Multiple Choice, Text, etc.
- Publish/unpublish with date controls
- K-anonymity threshold enforcement for reports

### 👥 **User Experience**
- Mobile-first responsive design with Tailwind + DaisyUI
- Progress tracking and autosave
- Clear anonymity badges on each question
- Optional follow-up opt-in for escrow questions
- Final comment section with anonymity choice

### 📈 **Reporting & Analytics**
- Response rate tracking and eNPS calculation
- Cohort analysis with k-anonymity protection
- Export to CSV, Excel, PDF
- Sentiment analysis for text responses
- Manager action note forms

### 🔒 **Safety & Privacy**
- Soft civility checking
- PII scrubbing on text inputs
- Role-based permissions (Owner, Admin, Creator, Analyst, Viewer)
- Secure token-based invitations

## Quick Start

### 1. Access the App
- **Public Surveys**: `/surveys/`
- **Admin Panel**: `/surveys/admin/`
- **Django Admin**: `/admin/surveys/`

### 2. Create Your First Survey
```bash
# Use the template survey
python manage.py seed_balanced_honesty

# Or create manually through admin interface
```

### 3. Publish and Invite
1. Edit survey in admin panel
2. Set publish dates and status
3. Send invitations via `/surveys/admin/{id}/invites/`
4. Share invite links with participants

## Question Types

| Type | Description | Anonymity Options |
|------|-------------|-------------------|
| **LIKERT** | Scale questions (1-5, 1-10) | All modes |
| **NPS** | Net Promoter Score (0-10) | All modes |
| **MULTI** | Multiple choice selection | All modes |
| **SINGLE** | Single choice selection | All modes |
| **SHORT_TEXT** | Short text input (500 chars) | All modes |
| **LONG_TEXT** | Long text input | All modes |
| **NUMBER** | Numeric input with range | All modes |
| **DATE** | Date picker | All modes |
| **RANK** | Ranking/ordering | All modes |

## Anonymity Modes Explained

### 🔒 **ANONYMOUS**
- Never stores `identity_user`
- Perfect for sensitive topics
- No follow-up possible
- Highest privacy protection

### 🔐 **ESCROW** (Default)
- Stores `identity_user` but hides in reports
- Optional follow-up opt-in
- Contact method collection
- Balanced privacy and accountability

### ✍️ **SIGNED**
- Stores `identity_user` and shows in reports
- Default `is_signed=True`
- For commitments and goals
- Full accountability

## K-Anonymity Protection

The app enforces k-anonymity for cohort-based reports:
- Minimum cohort size threshold (default: 5)
- Aggregated data only when threshold met
- Raw text hidden for small cohorts
- Signed answers bypass k-protection for that item only

## Permission Levels

| Role | Capabilities |
|------|--------------|
| **Owner** | Full control, delete surveys |
| **Admin** | Edit surveys, manage invites, view reports |
| **Creator** | Create and edit surveys |
| **Analyst** | View aggregated reports only |
| **Viewer** | View published surveys only |

## API Endpoints

- `GET /surveys/api/{id}/` - Survey details for mobile/JS
- `POST /surveys/admin/{id}/reorder-sections/` - HTMX reordering
- `POST /surveys/admin/{id}/reorder-questions/` - HTMX reordering

## Management Commands

```bash
# Seed the Balanced Honesty template survey
python manage.py seed_balanced_honesty

# Create sample data (future)
python manage.py create_sample_surveys

# Clean up test data (future)
python manage.py cleanup_test_data
```

## Template Survey: "Balanced Honesty"

The seeded template includes:

1. **Trust & Safety** (Escrow) - Workplace safety and trust
2. **Workload & Clarity** (Escrow) - Role clarity and work-life balance  
3. **Commitments** (Signed) - Goals and accountability
4. **eNPS & Open Floor** (Anonymous) - Overall satisfaction

## Customization

### Adding New Question Types
1. Extend `Question.QUESTION_TYPES` in models.py
2. Add form handling in `AnswerForm._build_fields()`
3. Update templates to render new types
4. Add validation in `QuestionForm.clean()`

### Custom Anonymity Modes
1. Extend `Question.ANONYMITY_MODES` in models.py
2. Update form logic in `AnswerForm._build_fields()`
3. Modify templates to show new badges
4. Update report generation logic

### Styling
- Uses Tailwind CSS + DaisyUI components
- Responsive design with mobile-first approach
- Custom CSS classes for anonymity badges
- HTMX for dynamic interactions

## Security Considerations

- CSRF protection on all forms
- User authentication required for admin functions
- Permission-based access control
- Secure token generation for invites
- Input validation and sanitization
- PII detection and scrubbing

## Future Enhancements

- [ ] Celery integration for scheduled reminders
- [ ] Advanced sentiment analysis
- [ ] Survey templates library
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration with external tools
- [ ] Webhook notifications
- [ ] Advanced reporting filters

## Contributing

1. Follow Django best practices
2. Maintain the mixed anonymity model integrity
3. Test with different user permission levels
4. Ensure mobile responsiveness
5. Update documentation for new features

## Support

For questions or issues:
1. Check the Django admin interface
2. Review the seeded template survey
3. Test with different anonymity modes
4. Verify k-anonymity enforcement in reports

---

**Built with Django 5.2, Tailwind CSS, DaisyUI, and HTMX**
