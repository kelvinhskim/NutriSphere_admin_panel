const UsersTableRow = ({ user }) => {
    return (
        <tr key={user.userID}>
            <td>{user.userID}</td>
            <td>{user.username}</td>
            <td>{user.email}</td>
            <td>{user.dailyCalorieGoal}</td>
            <td>
                <button class="edit-btn">✏️ Edit</button>
                <button class="delete-btn">❌ Delete</button>
            </td>
        </tr>
    )
}

export default UsersTableRow;