# Frontend Architecture & Components

## Component Hierarchy

```
App.jsx
├── Router
├── LoginPage
├── RegisterPage
├── ProtectedRoute
│   └── ChatPage
│       ├── Navbar
│       ├── ChatMessage (list)
│       └── Input Form
├── AdminRoute
│   └── AdminDashboard
│       ├── Navbar
│       ├── Routes
│       ├── AdminStats
│       └── AdminDocs
└── NotFoundPage
```

## Page Components

### LoginPage (`src/pages/LoginPage.jsx`)
- User login form
- Email/password validation
- JWT token handling
- Demo credentials display
- Error messages

### RegisterPage (`src/pages/RegisterPage.jsx`)
- User registration form
- Password confirmation
- Name field
- Auto-login after registration
- Error handling

### ChatPage (`src/pages/ChatPage.jsx`)
- Main chat interface for students
- Message history display
- Question input with multiline support
- Source documents display
- Loading states
- Error handling
- Auto-scroll to latest messages

### AdminDashboard (`src/pages/AdminDashboard.jsx`)
- Admin panel with routing
- Dashboard stats view
- Document management view
- Statistics display

## Reusable Components

### Navbar (`src/components/Navbar.jsx`)
- Logo and branding
- Navigation links
- User info display
- Logout button
- Mobile menu
- Role-based navigation

### ChatMessage (`src/components/ChatMessage.jsx`)
- Message display with role differentiation
- Markdown rendering
- Source documents list
- Confidence scores
- Animations

### ProtectedRoute (`src/components/ProtectedRoute.jsx`)
- Authentication check
- Redirect to login if not authenticated
- Wraps protected pages

### AdminRoute (`src/components/AdminRoute.jsx`)
- Admin role check
- Redirect to chat if not admin
- Wraps admin pages

### AdminDocs (`src/components/AdminDocs.jsx`)
- Document upload form
- Document listing table
- Delete functionality
- File type validation
- Size validation

## State Management (Zustand)

### useAuthStore
```javascript
{
  user,           // Current user object
  token,          // JWT token
  isAuthenticated, // Boolean
  setAuth,        // Set user and token
  logout,         // Clear auth
  setUser         // Update user
}
```

### useChatStore
```javascript
{
  messages,       // Array of messages
  isLoading,      // Loading state
  error,          // Error message
  addMessage,     // Add to messages
  setMessages,    // Replace messages
  clearMessages,  // Clear all
  setLoading,     // Set loading
  setError        // Set error
}
```

### useDocumentStore
```javascript
{
  documents,      // Array of documents
  isLoading,      // Loading state
  error,          // Error message
  setDocuments,   // Set documents
  addDocument,    // Add document
  removeDocument, // Remove document
  setLoading,     // Set loading
  setError        // Set error
}
```

## API Service Layer

### Authentication
```javascript
authService.register(email, name, password)
authService.login(email, password)
```

### Documents
```javascript
documentService.uploadDocument(file, title, description)
documentService.getDocuments(skip, limit)
documentService.getDocument(id)
documentService.updateDocument(id, data)
documentService.deleteDocument(id)
documentService.searchDocuments(query, skip, limit)
```

### Queries
```javascript
queryService.askQuestion(question, relevantDocuments)
queryService.getQueryHistory(skip, limit)
queryService.getQuery(id)
```

### Admin
```javascript
adminService.getDashboardStats()
adminService.getUsers(skip, limit)
adminService.getDocumentStats()
adminService.getQueryStats()
```

## Styling

### Tailwind CSS
- Utility-first CSS framework
- Responsive design
- Dark mode capable
- Custom animations

### Key Classes
- `.message-enter`: Slide-in animation
- `.prose`: Markdown styling
- `.scrollbar-hide`: Hide scrollbars

## Error Handling

### API Errors
- Axios interceptor catches 401 (unauthorized)
- Automatic logout and redirect to login
- User-friendly error messages
- Error state in stores

### Form Validation
- Email validation
- Password strength checking
- File type/size validation
- Required field validation

## Performance Optimizations

### Code Splitting
- Page components lazy loaded with React.lazy
- Route-based code splitting

### Memoization
- useMemo for expensive computations
- useCallback for event handlers

### Caching
- localStorage for auth data
- API response caching (can be added)

## Accessibility

### ARIA Labels
- Form labels linked to inputs
- Button purposes clear
- Error messages announced

### Keyboard Navigation
- Tab order logical
- Enter to submit forms
- Escape to close modals

### Contrast
- WCAG AA standards
- Clear color differentiation

## Development

### Build Commands
```bash
npm run dev      # Dev server with hot reload
npm run build    # Production build
npm run preview  # Preview build locally
npm run lint     # Lint code (can be added)
```

### Environment Variables
```
VITE_API_BASE_URL=http://localhost:8000/api
```

### Main Dependencies
- react: UI framework
- react-router-dom: Client routing
- axios: HTTP client
- zustand: State management
- tailwindcss: Styling
- lucide-react: Icons
- react-markdown: Markdown rendering
