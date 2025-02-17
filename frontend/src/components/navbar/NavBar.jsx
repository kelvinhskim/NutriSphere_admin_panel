import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <header>
      <div>
        <Link to="/">
        </Link>
      </div>

      <h1>My website name</h1>
      
      <nav>
        <ul>
          <li>
            <Link to="/">Home</Link>
          </li>
          <li>
            <Link to="/"></Link>
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Navbar;
