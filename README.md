# EV Conversion Project Management System

A quick and dirty Python-based system for generating test ev-projects using Supabase as the backend.
It will create reasonably random projects using fake data and vehicle images from a large dataset of images. You'll need to get a copy of those images/folders from Mike - there's 8500 images, too much for a git repo.

You'll need to manually create a .env in  the top folder with the following values populated:

```
    API_KEY="..."
    SUPABASE_URL="..."
    SUPABASE_KEY="..."
    ELCTROMOTIVE_USER="..."
    ELCTROMOTIVE_PASSWORD="..."
    ELECTROMOTIVE_URL='..."
    ELECTROMOTIVE_LOGIN_URL='..."
    TODO_CLUSTER_ID =..."
```

You'll also need to install all the python requirements:
```
pip install -r requirements
```

## Features

- **Authentication & Session Management**: Handles user authentication with Supabase
- **Project Management**: Create and manage EV conversion projects with detailed specifications
- **Component Tracking**: Track conversion components, vendors, costs, and delivery status
- **Timeline Management**: Document project progress with photos, notes, and milestones
- **Phase Tracking**: Manage conversion phases and tasks
- **Image Hosting**: Upload vehicle images to Freeimage.host with automatic retry logic

## Project Structure

```
.
├── main.py                          # Main entry point
├── WebsiteTester.py                 # Authentication and API interaction handler
├── supabaseclient.py                # Supabase client for project management
├── util/
│   ├── build-image-index.py         # Build JSON index of vehicle images
│   └── upload-to-freeimage.py       # Upload images to Freeimage.host
├── requirements.txt                 # Python dependencies
└── lists.json                       # Reference data (components, vendors, etc.)
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/MikeMontana1968/elelctr0motive-test-project-builder.git
cd elelctr0motive-test-project-builder
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

**Windows:**
```bash
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the root directory:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
FREEIMAGE_API_KEY=your_freeimage_api_key
```

## Usage

### Run the main application

```bash
python main.py
```

### Build image index

```bash
python util/build-image-index.py
```

### Upload images to Freeimage.host

```bash
python util/upload-to-freeimage.py
```

## Dependencies

- **beautifulsoup4**: HTML parsing
- **requests**: HTTP requests
- **supabase**: Supabase Python client
- **wonderwords**: Random sentence generation
- **faker**: Fake data generation
- **faker-vehicle**: Vehicle data generation
- **python-dotenv**: Environment variable management

See [requirements.txt](requirements.txt) for complete list.

## Database Schema

The system works with the following Supabase tables:

- `projects`: Main project information
- `project_phases`: Conversion phases for each project
- `project_tasks`: Tasks within each phase
- `project_components`: Parts and components tracking
- `project_timeline_entries`: Project progress documentation

## Notes

- The `vehicle-images/` folder (8500+ JPGs) is excluded from version control
- Images are hosted externally via Freeimage.host
- Session data and generated datasets are also gitignored

## License

MIT
