# EV Conversion Project Management System

A quick and dirty Python-based system for generating test ev-projects using Supabase as the backend.
It will create reasonably random projects with  fake data and vehicle images from a large dataset of images. You'll need to get a copy of those images/folders from Mike - there's 8500 images, too much for a git repo.


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
    API_KEY="..."
    SUPABASE_URL="..."
    SUPABASE_KEY="..."
    ELCTROMOTIVE_USER="..."
    ELCTROMOTIVE_PASSWORD="..."
    ELECTROMOTIVE_URL='..."
    ELECTROMOTIVE_LOGIN_URL='..."
    TODO_CLUSTER_ID ="2233c641-866e-460c-ba16-facce4bbdde4"
```
API_KEY is your FreeImage API key (sign up and its free)
ELCTROMOTIVE_USER is the user to whom the projects will be created-for. Account must previously exist.

The ClusterID used is for "NY/NJ/PA EV Builders". Change to your liking.


## Usage

### After unzipping all the images to \vehicle-paths, run these two utils to build a json file of all the images,
and the 2nd one will upload them to FreeImage (get your own free API key from there).

Note it takes A LONG TIME to upload the images, and FreeImage will rate limit you. When it happens the code gets a 403 error and stops. After a few hours, re-run the upload script, and it will pick up where it left off.
Right now the uploader script does some goofy random-skip-through-the-list so that the uploaded images will be spread out across the alphabet of makes/models.

```bash
cd util
python build-image-index.py
python upload-to-freeimage
```

### Run the main application

Review the code to see how many counts of each sub items are generated, and you'll discover most of the list-elements come from "./lists.json" which you can customize to your liking. 

```bash
python main.py
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
