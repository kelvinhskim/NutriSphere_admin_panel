import React from 'react';
import { Link } from 'react-router-dom';

function HomePage() {
    return (
        <main className="container">
            <section className="welcome-section">
                <h2>Welcome to NutriSphere's Admin Portal</h2>
                <p>Your ultimate solution for managing the database behind our users' nutrition metrics and exercise patterns.</p>
                <Link to='/users' className="btn">Get Started</Link>
            </section>
        </main>
    )
}

export default HomePage;