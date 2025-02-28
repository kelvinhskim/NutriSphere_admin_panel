const UsersTableRow = ({ user }) => {
    return (
        <tr key={user.userID}>
            <td>{user.userID}</td>
            <td>{user.username}</td>
            <td>{user.email}</td>
            <td>{user.dailyCalorieGoal}</td>
            <td>
                <button className="edit-btn">✏️ Edit</button>
                <button className="delete-btn">❌ Delete</button>
            </td>
        </tr>
    )
}

export default UsersTableRow;