# 🎵 Suno Prompt Builder

A Django app for managing Suno song prompt data locally and preparing for future API integration when Suno releases a public API.

## Features

- **Song Prompt Management**: Create, save, and manage song prompts with all Suno parameters
- **Beautiful UI**: Modern interface built with Tailwind CSS and DaisyUI
- **Real-time JSON Preview**: See your prompt formatted as JSON as you type
- **Copy to Clipboard**: One-click copying of formatted prompts
- **Admin Interface**: Full Django admin integration for prompt management
- **Future-Ready**: Prepared for Suno API integration when available

## Models

### SongPrompt

The main model for storing song prompts with the following fields:

- `title` (CharField): Song title
- `lyrics` (TextField): Song lyrics (optional)
- `subject` (CharField): Song concept description
- `styles` (JSONField): List of musical styles (e.g., ['disco', 'rap', 'cinematic'])
- `excluded_styles` (JSONField): Styles to exclude
- `weirdness` (PositiveSmallIntegerField): 0-100 scale for song weirdness
- `style_influence` (PositiveSmallIntegerField): 0-100 scale for style influence
- `is_instrumental` (BooleanField): Whether the song is instrumental
- `created_at` (DateTimeField): Creation timestamp
- `updated_at` (DateTimeField): Last update timestamp

## Installation

1. Add `'suno_prompt_builder'` to your `INSTALLED_APPS` in `settings.py`
2. Include the URLs in your main `urls.py`:
   ```python
   path('suno-prompt-builder/', include('suno_prompt_builder.urls')),
   ```
3. Run migrations:
   ```bash
   python manage.py makemigrations suno_prompt_builder
   python manage.py migrate
   ```

## Usage

### Web Interface

Visit `/suno-prompt-builder/` to access the main interface where you can:

- Fill out the song prompt form
- See real-time JSON preview
- Copy formatted prompts to clipboard
- Save prompts to the database

### Admin Interface

Access `/admin/` to manage saved prompts with full CRUD operations.

### Management Commands

Seed the database with example prompts:
```bash
python manage.py seed_prompts
```

## API Integration

The app includes a stub file (`suno_api_stub.py`) for future Suno API integration. When Suno releases their public API:

1. Replace the mock implementations in `SunoAPIClient`
2. Add your API key to Django settings:
   ```python
   SUNO_API_KEY = 'your_api_key_here'
   SUNO_API_BASE_URL = 'https://api.suno.ai/v1'
   ```
3. Uncomment the actual API calls in the stub file

## File Structure

```
suno_prompt_builder/
├── __init__.py
├── admin.py              # Admin interface configuration
├── apps.py               # App configuration
├── models.py             # SongPrompt model
├── views.py              # Web interface views
├── urls.py               # URL routing
├── suno_api_stub.py      # Future API integration
├── management/
│   └── commands/
│       └── seed_prompts.py  # Management command
├── static/
│   └── suno_prompt_builder/
│       └── js/
│           └── copy_prompt.js  # JavaScript functionality
└── templates/
    └── suno_prompt_builder/
        └── prompt_builder.html  # Main interface template
```

## Dependencies

- Django 5.2+
- Tailwind CSS (via django-tailwind)
- DaisyUI (for UI components)

## Example Usage

### Creating a Prompt via Python

```python
from suno_prompt_builder.models import SongPrompt

prompt = SongPrompt.objects.create(
    title="Midnight Disco Dreams",
    subject="A disco song about dancing in the city at night",
    styles=['disco', 'funk', 'electronic'],
    excluded_styles=['heavy metal', 'country'],
    weirdness=30,
    style_influence=80,
    is_instrumental=False
)

# Get formatted prompt for API
formatted = prompt.formatted_prompt()
print(formatted)
```

### Future API Integration

```python
from suno_prompt_builder.suno_api_stub import create_song_from_prompt

# When Suno API is available
response = create_song_from_prompt(prompt.formatted_prompt())
print(f"Song ID: {response['id']}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.