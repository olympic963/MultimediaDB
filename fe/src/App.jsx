import './App.css'
import { useState } from "react";
import NavBar from './components/NavBar'
import SearchBar from './components/SearchBar'
import LoginForm from "./components/LoginForm";
function App() {
  const [isLoginOpen, setIsLoginOpen] = useState(false);

  return (
    <div className="flex flex-col items-center justify-center h-screen space-y-6">
      <NavBar setIsLoginOpen={setIsLoginOpen} />
      {isLoginOpen && <LoginForm setIsLoginOpen={setIsLoginOpen} />}
      <img 
        src="src/assets/Logo.png" 
        alt="React logo" 
        className="w-auto h-[10%]" 
      />
      <SearchBar />
    </div>
  )
}

export default App
