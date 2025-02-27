import { useState, useEffect } from 'react';
import axios from 'axios';

const Users = () => {
    console.log('hi users')
    const [usersData, setUsersData] = useState([]);

    const getUserData = () => {
        const URL = import.meta.env.VITE_API_URL + 'users';
        console.log("API URL:", URL);
        axios.get(URL)
        .then((response) => {
            console.log(response.data)
            setUsersData(response.data)
        })
        .catch((error) => {
            console.log('Error fetching users:', error);
        })
    }

    useEffect(() => {
        getUserData();
    }, [])

    return (
        <main>
            <h2>Browse Users</h2>
            <table border="1">
                <thead>
                    <tr>
                        <th>User ID</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Daily Calorie Goal</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>Tyler</td>
                        <td>tyler@oregonstate.edu</td>
                        <td>2400</td>
                        <td>
                            <button class="edit-btn">✏️ Edit</button>
                            <button class="delete-btn">❌ Delete</button>
                        </td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td>Jane</td>
                        <td>jane@oregonstate.edu</td>
                        <td>2000</td>
                        <td>
                            <button class="edit-btn">✏️ Edit</button>
                            <button class="delete-btn">❌ Delete</button>
                        </td>
                    </tr>
                    <tr>
                        <td>3</td>
                        <td>Alex</td>
                        <td>alex@oregonstate.edu</td>
                        <td>2200</td>
                        <td>
                            <button class="edit-btn">✏️ Edit</button>
                            <button class="delete-btn">❌ Delete</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </main>
    );
}

export default Users;