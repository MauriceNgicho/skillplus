import { StrictMode } from 'react'  // detect bug in development mode.
import { createRoot } from 'react-dom/client'  // createRoot is the new API for rendering in React 18 and later. It replaces the older ReactDOM.render method and provides better performance and support for concurrent features.
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
