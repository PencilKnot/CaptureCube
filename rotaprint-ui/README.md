# RotaPrint UI - 3D Scanning Interface

A modern React application for managing 3D scans with automated model generation and listing creation.

## Features

### 🔥 Core Functionality
- **Image Upload Interface**: Drag-and-drop or click-to-upload multiple images
- **Real-time Scan Processing**: Visual progress indicators for upload and processing stages
- **Mock 3D Model Generation**: Simulates OpenMVG + OpenMVS pipeline workflow
- **AI-Generated Descriptions**: Mock AI descriptions for scanned objects
- **Hardware Measurements**: Precise measurements display for hardware parts
- **Automatic Listing Creation**: Auto-generates product listings after scan completion

### 📱 User Interface
- **Clean, Professional Design**: Built with Tailwind CSS
- **Responsive Layout**: Works on desktop and mobile devices
- **Real-time Status Updates**: Live progress tracking with animated indicators
- **Interactive 3D Model Viewer**: Modal viewer for GLB files (placeholder implementation)
- **Intuitive Workflow**: Step-by-step scanning process

### 🔧 Technical Features
- **TypeScript**: Full type safety throughout the application
- **React 19**: Latest React features and hooks
- **Mock State Management**: Simulated backend workflow for demo purposes
- **Extensible Architecture**: Ready for real backend integration

## Getting Started

### Prerequisites
- Node.js (v18 or higher)
- npm

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint
```

### Development Server
The app will be available at `http://localhost:5173/`

## Architecture

### Components
- **App.tsx**: Main application component with scan management
- **ModelViewer.tsx**: 3D model display component (placeholder for Three.js integration)
- **ModelViewerModal.tsx**: Full-screen model viewing modal

### Data Flow
1. User uploads images and provides scan name
2. System simulates upload progress (OpenMVG + OpenMVS workflow)
3. Mock 3D model generation with AI description
4. Automatic listing creation with measurements
5. Interactive model viewing capability

### Mock Backend Simulation
The app simulates a complete 3D scanning pipeline:
- Image upload progress tracking
- 3D reconstruction processing
- AI description generation
- Hardware part measurements
- GLB model file handling

## Future Enhancements

### Ready for Integration
- **Real Backend API**: Replace mock functions with actual API calls
- **Three.js Integration**: Replace placeholder with real GLB model viewer
- **File Upload Service**: Connect to actual image upload endpoints
- **AI Services**: Integrate real AI description generation
- **Measurement Tools**: Add interactive measurement capabilities
- **Export Features**: Add model download and sharing functionality

### Potential Features
- Batch scanning support
- Advanced model editing tools
- Real-time collaboration
- Cloud storage integration
- Mobile app companion

## Technology Stack

- **React 19** - Modern UI library
- **TypeScript** - Type safety and developer experience
- **Tailwind CSS** - Utility-first styling
- **Vite** - Fast build tool and dev server
- **ESLint** - Code quality and consistency
