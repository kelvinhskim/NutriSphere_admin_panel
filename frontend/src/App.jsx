import { useState } from 'react'
import { Routes, Route } from "react-router-dom";
import Navbar from './components/navbar/NavBar';
import HomePage from './pages/HomePage.jsx';
import Users from './pages/Users.jsx';
import './App.css'

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path='/' element={<HomePage />} />
        <Route path='/users/*' element={<Users />} />
      </Routes>
    </>
  );
}

export default App
