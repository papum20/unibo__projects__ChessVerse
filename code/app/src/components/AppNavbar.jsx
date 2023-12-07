import PropTypes from 'prop-types';
import { Navbar, Nav, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const AppNavbar = ({ user, onSignOut }) => {
	
  return (

    <Navbar bg="light" expand="md">

		<Navbar.Brand href="#home">My App</Navbar.Brand>
		
		<Navbar.Toggle aria-controls="basic-navbar-nav" />
		
		<Navbar.Collapse id="basic-navbar-nav">
			<Nav className="ml-auto">
			{user ? (
				<>
				<Nav.Link href="#profile">{user.name}</Nav.Link>
				<Nav.Link href="#profile">
					<img src={user.picture} alt="Profile" style={{ borderRadius: '50%', width: '30px', height: '30px' }} />
				</Nav.Link>
				<Button variant="outline-danger" onClick={onSignOut}>Sign Out</Button>
				</>
			) : (
				<>
				<Nav.Link href="#login">Guest (not logged)</Nav.Link>
				<Link to="/login">
					<Button variant="outline-primary">Login</Button>
				</Link>
				</>
			)}
			</Nav>
		</Navbar.Collapse>

    </Navbar>
  );
};

AppNavbar.propTypes = {
  user: PropTypes.shape({
    name: PropTypes.string,
    picture: PropTypes.string,
  }),
  onSignOut: PropTypes.func.isRequired,
};

export default AppNavbar;