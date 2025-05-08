import './App.css'
import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import SearchBar from './components/SearchBar';
import LoginForm from './components/LoginForm';
import ResultPage from './components/ResultPage';
import Loading from './components/Loading';

function App() {
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  return (
    <Router>
      <div className="flex flex-col items-center justify-center h-screen space-y-6">
        <NavBar setIsLoginOpen={setIsLoginOpen} />
        {isLoginOpen && <LoginForm setIsLoginOpen={setIsLoginOpen} />}
        <Routes>
          <Route
            path="/"
            element={
              <>
                <img 
                  src="src/assets/Logo.png" 
                  alt="React logo" 
                  className="w-auto h-[10%]" 
                />
                <SearchBar setIsLoading={setIsLoading} setError={setError} />
                {isLoading && !error && <Loading />}
                {error && (
                  <div className="text-red-500 bg-red-50 px-4 py-2 rounded-lg border border-red-200">
                    {error}
                  </div>
                )}
              </>
            }
          />
          <Route path="/results" element={<ResultPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;