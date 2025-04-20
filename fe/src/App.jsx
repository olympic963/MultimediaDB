import './App.css'
import { useState, useEffect } from "react";
import NavBar from './components/NavBar'
import SearchBar from './components/SearchBar'
import LoginForm from "./components/LoginForm";
import ResultsPage from './components/ResultPage';

function App() {
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  useEffect(() => {
    const onLocationChange = () => {
      setCurrentPath(window.location.pathname);
    };

    window.addEventListener('popstate', onLocationChange);

    return () => {
      window.removeEventListener('popstate', onLocationChange);
    };
  }, []);

  return (
    <div className="flex flex-col items-center justify-center h-screen space-y-6">
      <NavBar setIsLoginOpen={setIsLoginOpen} />
      {isLoginOpen && <LoginForm setIsLoginOpen={setIsLoginOpen} />}
      <img 
        src="src/assets/Logo.png" 
        alt="React logo" 
        className="w-auto h-[10%]" 
      />
      {currentPath === "/" && <SearchBar />}
      {currentPath === "/results" && <ResultsPage />}
    </div>
  )
}

export default App
