# Modern Django Dashboard with Site-Wide Search

A comprehensive Django application featuring a modern dashboard interface and a future-proof site-wide search system that automatically indexes all content across the entire application.

## 🚀 Features

### Modern Dashboard
- **Personalized Welcome**: Dynamic greeting with user information
- **Statistics Cards**: Real-time counts of files, images, prompts, and searches
- **Quick Actions**: One-click access to common tasks
- **Recent Activity**: Timeline of user's recent actions
- **Recent Content**: Latest files, images, and prompts
- **Popular Categories**: Trending prompt categories
- **Search History**: User's recent search queries

### Site-Wide Search (Ctrl+K)
- **Global Search Modal**: Accessible via Ctrl+K shortcut or search button
- **Real-time Results**: Instant search results as you type
- **Smart Filtering**: Filter by app, model type, and content
- **Search Suggestions**: Popular searches and user history
- **Highlighted Results**: Search terms highlighted in results
- **Future-Proof**: Automatically indexes new apps and models

### Search Features
- **Comprehensive Indexing**: Searches across all apps and models
- **Weighted Results**: Featured content appears higher in results
- **Rich Metadata**: Includes file types, categories, tags, and more
- **Search Analytics**: Track popular searches and user behavior
- **Admin Interface**: Manage search index and view statistics

## 🛠 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

3. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Build Tailwind CSS**
   ```bash
   python manage.py tailwind build
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Rebuild search index**
   ```bash
   python manage.py rebuild_search_index --clear
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 📱 Usage

### Dashboard
- Visit the homepage to see your personalized dashboard
- Use quick action buttons to upload files, images, or create prompts
- View your recent activity and content statistics
- Browse popular categories and recent searches

### Search
- Press **Ctrl+K** (or Cmd+K on Mac) to open the global search modal
- Type to search across all content in real-time
- Use filters to narrow down results by app or content type
- Click on search suggestions for quick access
- View detailed search results with highlighted terms

### Admin Interface
- Access `/admin/` to manage the search index
- View search statistics and user behavior
- Manage featured search suggestions
- Monitor search performance

## 🔧 Configuration

### Search Index Management

**Rebuild entire index:**
```bash
python manage.py rebuild_search_index --clear
```

**Rebuild specific app:**
```bash
python manage.py rebuild_search_index --app files
```

**Add search to new models:**

1. Add `get_search_content()` method to your model:
```python
def get_search_content(self):
    return {
        'title': self.title,
        'content': f"{self.title} {self.description}",
        'description': self.description,
        'url': f'/your-app/{self.id}/',
        'weight': 1,
        'is_public': True,
        'fields': {
            'custom_field': self.custom_field,
        }
    }
```

2. Rebuild the search index:
```bash
python manage.py rebuild_search_index --app your-app
```

### Customizing Search Weights

Models can specify search weights in their `get_search_content()` method:
- **Weight 1**: Standard content
- **Weight 2**: Important content (PDFs, images, featured prompts)
- **Weight 3**: Featured content

### Search API Endpoints

- `GET /search/api/?q=query&limit=10` - Real-time search results
- `GET /search/suggestions/?q=query` - Search suggestions
- `GET /search/autocomplete/?q=query` - Autocomplete terms
- `GET /search/stats/` - Search statistics (authenticated)
- `POST /search/rebuild/` - Rebuild search index (authenticated)

## 🏗 Architecture

### Search System
- **SearchIndex Model**: Generic content type for indexing any model
- **SearchHistory Model**: Tracks user search behavior
- **SearchSuggestion Model**: Manages popular search terms
- **Automatic Indexing**: New content is automatically indexed
- **Future-Proof**: Works with any new app or model

### Dashboard System
- **Dynamic Content**: Real-time statistics and recent activity
- **User-Specific Data**: Personalized content based on user actions
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Built with Tailwind CSS and DaisyUI

## 📊 Models Included

### Files App
- File upload and management
- File type detection
- Size and metadata tracking

### Images App
- Image upload and gallery
- Automatic thumbnail generation
- Image metadata extraction

### Prompts App
- AI prompt management
- Categories and tags
- Usage tracking and ratings

### UserProfile App
- Extended user profiles
- Avatar management
- Professional information

### Search App
- Site-wide search functionality
- Search analytics
- Search suggestions

## 🎨 Styling

The application uses:
- **Tailwind CSS**: Utility-first CSS framework
- **DaisyUI**: Component library for Tailwind
- **Heroicons**: Beautiful SVG icons
- **Responsive Design**: Mobile-first approach

## 🔒 Security

- **Authentication Required**: Dashboard and search features require login
- **CSRF Protection**: All forms protected against CSRF attacks
- **Input Validation**: All search queries are validated
- **Rate Limiting**: Search API includes basic rate limiting

## 🚀 Deployment

1. **Set up production database**
2. **Configure static files**
3. **Set environment variables**
4. **Run migrations**
5. **Rebuild search index**
6. **Set up periodic search index updates**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the documentation
- Search existing issues
- Create a new issue with details

---

**Built with ❤️ using Django, Tailwind CSS, and modern web technologies.**