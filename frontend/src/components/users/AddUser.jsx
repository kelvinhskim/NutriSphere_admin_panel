import axios from 'axios';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const AddUser = ({ getUserData }) => {
    const navigate = useNavigate();

    const [userFormData, setUserFormData] = useState({
        username: '',
        email: '',
        dailyCalorieGoal: ''
    })

    const handleSubmit = (e) => {
        e.preventDefault()
        const newUser = {
            username: userFormData.username,
            email: userFormData.email,
            dailyCalorieGoal: Number(userFormData.dailyCalorieGoal)
        };
        console.log('USER Form Data:', newUser)

        const URL = import.meta.env.VITE_API_URL + "users";
        console.log("API POST URL:", URL, newUser);
        axios.post(URL, newUser)
        .then((response) => {
            navigate('/users');
            getUserData()
            console.log(response.data)
        })
        .catch((error) => {
            console.log('Error creating user:', error)
        })
    }

    const handleInputChange = (e) => {
        console.log('input change', e.target)
        const { name, value } = e.target
        setUserFormData((prevState) => ({
            ...prevState,
            [name]: value
        }))
    }
    
    return (
        <>
            <h2>Add a New User</h2>
            <form onSubmit={handleSubmit}>
                <label htmlFor="username">Username:</label>
                <input type="text" id="username" name="username" value={userFormData.username} onChange={handleInputChange} required />

                <label htmlFor="email">Email:</label>
                <input type="email" id="email" name="email" value={userFormData.email} onChange={handleInputChange} required />

                <label htmlFor="calorieGoal">Daily Calorie Goal:</label>
                <input type="number" id="calorieGoal" name="dailyCalorieGoal" value={userFormData.dailyCalorieGoal} onChange={handleInputChange} required />

                <button type="submit">➕ Add</button>
            </form>
        </>
    );
}

export default AddUser;