import "./App.css";
import { Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import Navbar from "./components/navbar/NavBar";
import Users from "./pages/Users";
import DailyTrackers from "./pages/DailyTrackers";
import FoodItems from "./pages/FoodItems";
import FoodEntries from "./pages/FoodEntries";
import Exercises from "./pages/Exercises";

function App() {
  console.log('App is running')

  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/Users" element={<Users />} />
        <Route path="/DailyTrackers" element={<DailyTrackers />} />
        <Route path="/FoodItem" element={<FoodItems />} />
        <Route path="/FoodEntries" element={<FoodEntries />} />
        <Route path="/Exercises" element={<Exercises />} />
      </Routes>
    </>
  );
}

export default App;
