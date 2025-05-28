# Orbyte - Decentralized GPU Rental Platform

Orbyte is a platform that allows users to rent out their idle GPUs for running GenAI workloads, while others can submit tasks to be executed on the network. Payments are handled using a mock cryptocurrency system.

## Features

- **GPU Registration**: Users can register their GPUs with specifications and pricing
- **Task Submission**: Submit AI/ML tasks to be executed on available GPUs
- **Payment System**: Mock cryptocurrency payments for GPU usage
- **User Authentication**: Secure user registration and authentication
- **Task Management**: Track and manage your submitted tasks
- **GPU Management**: Monitor and manage your registered GPUs

## Tech Stack

- **Backend**: Python with FastAPI
- **Database**: SQLite (with SQLAlchemy ORM)
- **Authentication**: JWT (JSON Web Tokens)
- **Frontend**: Typescript + Svelte + TailwindCSS
- **Containerization**: Docker (To be implemented)

## Getting Started

### Prerequisites

#### Backend
- Python 3.11
- pip (Python package manager)

#### Frontend
- Node.js 18+ (includes npm)
- pnpm (recommended) or npm

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nMaroulis/orbyte.git
   cd orbyte
   ```

2. **Set up a virtual environment (recommended)**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the `backend` directory with the following content:
   ```
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///./orbyte.db
   ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
   ```

### Running the Application

#### Backend

1. **Start the backend server**
   ```bash
   # From the project root
   ./run.sh
   ```

2. **Access the API documentation**
   - Open your browser and go to: http://localhost:8000/api/docs
   - This will show the interactive Swagger/OpenAPI documentation

#### Frontend

1. **Install frontend dependencies**
   ```bash
   # From the project root
   cd frontend
   pnpm install  # or npm install if not using pnpm
   ```

2. **Set up environment variables**
   Create a `.env` file in the `frontend` directory with:
   ```
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

3. **Start the development server**
   ```bash
   pnpm dev  # or npm run dev
   ```
   - The frontend will be available at: http://localhost:5173
   - The page will reload when you make changes

4. **Build for production**
   ```bash
   pnpm build  # or npm run build
   pnpm preview  # to preview the production build
   ```

### Development

#### Frontend Tech Stack

- **Framework**: Svelte 4
- **Language**: TypeScript 5
- **Styling**: TailwindCSS 3
- **State Management**: Svelte stores
- **HTTP Client**: Built-in fetch API with custom wrapper
- **Form Handling**: HTML5 form validation with custom components
- **Routing**: SvelteKit file-based routing

#### Available Scripts

- `dev`: Start development server
- `build`: Build for production
- `preview`: Preview production build
- `check`: Run type checking
- `check:watch`: Run type checking in watch mode
- `lint`: Run ESLint
- `format`: Format code with Prettier

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/token` - Login and get access token
- `GET /api/auth/me` - Get current user details

### GPUs
- `GET /api/gpus/` - List all available GPUs
- `POST /api/gpus/` - Register a new GPU
- `GET /api/gpus/{gpu_id}` - Get GPU details
- `PUT /api/gpus/{gpu_id}` - Update GPU details
- `DELETE /api/gpus/{gpu_id}` - Delete a GPU

### Tasks
- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Submit a new task
- `GET /api/tasks/{task_id}` - Get task details
- `POST /api/tasks/{task_id}/cancel` - Cancel a task

### Payments
- `GET /api/payments/` - List all payments
- `GET /api/payments/sent` - List sent payments
- `GET /api/payments/received` - List received payments
- `GET /api/payments/{payment_id}` - Get payment details
- `POST /api/payments/{task_id}/pay` - Create a payment for a task

## Project Structure

```
orbyte/
├── backend/                  # Backend application
│   ├── core/                 # Core functionality
│   ├── models/               # Database models
│   └── ...
│
├── frontend/                 # Frontend application
│   ├── src/
│   │   ├── lib/             # Shared utilities and components
│   │   ├── routes/           # Application routes (pages)
│   │   ├── app.css          # Global styles
│   │   └── app.html          # Main HTML template
│   ├── static/              # Static assets
│   ├── .env                 # Frontend environment variables
│   ├── package.json         # Dependencies and scripts
│   └── ...
│
└── ...
│   ├── routers/              # API routes
│   ├── schemas/              # Pydantic models
│   ├── services/             # Business logic
│   ├── database.py           # Database configuration
│   ├── init_db.py            # Database initialization
│   ├── main.py               # FastAPI application
│   └── requirements.txt      # Python dependencies
└── README.md                 # This file
```

## Development

### Running Tests
```bash
pytest
```

### Code Style
This project uses `black` for code formatting and `isort` for import sorting.

```bash
pip install black isort
black .
isort .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Improvements

- Implement a real blockchain payment system
- Add more sophisticated GPU scheduling and load balancing
- Implement user roles and permissions
- Add more comprehensive tests
- Implement a React frontend
- Add Docker support for easy deployment
- Implement WebSocket for real-time updates
- Add monitoring and logging
- Implement rate limiting and API keys

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
