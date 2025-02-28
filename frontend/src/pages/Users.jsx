import { useState, useEffect } from 'react';
import axios from 'axios';
import UsersTableRow from '../components/users/UsersTableRow';
import AddUser from '../components/users/AddUser';

const Users = () => {
    console.log('hi users')
    const [usersData, setUsersData] = useState([]);

    const getUserData = () => {
        const URL = import.meta.env.VITE_API_URL + 'users';
        console.log("API GET URL:", URL);
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
        <>
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
                        {usersData.map((user) => (
                            <UsersTableRow 
                                key={user.userID}
                                user={user}
                            />
                        ))}
                    </tbody>
                </table>
            </main>
            <section>
                <AddUser />
            </section>
        </>
    );
}

export default Users;