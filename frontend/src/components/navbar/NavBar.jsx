import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <header>
      <div>
        <Link to="/">
        </Link>
      </div>

      <h1>NutriSphere</h1>

      <nav>
        <ul>
          <li>
            <Link to="/">Home</Link>
          </li>
          <li>
            <Link to="/">Users</Link>
          </li>
          <li>
            <Link to="/">Daily Trackers</Link>
          </li>
          <li>
            <Link to="/">Daily Trackers</Link>
          </li>
          <li>
            <Link to="/">Food Items</Link>
          </li>
          <li>
            <Link to="/">Food Entries</Link>
          </li>
          <li>
            <Link to="/">Exercise</Link>
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Navbar;
