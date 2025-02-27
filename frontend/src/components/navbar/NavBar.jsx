import { Link } from 'react-router-dom';

const Navbar = () => {
    return (
        <header>
            <h1>NutriSphere: A Comprehensive Calorie Tracking System</h1>
            <nav>
                <Link to='/'>🏠 Home</Link>
                <Link to='/users'>👤 Users</Link>
            </nav>
        </header>
    );
}

export default Navbar;