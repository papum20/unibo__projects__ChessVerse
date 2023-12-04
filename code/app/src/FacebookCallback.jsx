import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const FacebookCallback = () => {
  const location = useLocation();
  const navigateTo = useNavigate();

  useEffect(() => {
    const handleFacebookResponse = async () => {
      try {
        // Extract the authorization code from the URL
        const params = new URLSearchParams(location.search);
        const code = params.get('code');

        // Make a request to your server to exchange the code for an access token
        const response = await fetch(`/api/auth/facebook/callback?code=${code}`, {
          method: 'POST',
          // Include any additional headers or authentication tokens if needed
        });

        // Parse the response (which might include the user data)
        const data = await response.json();

        // Handle the user data or perform other actions
        console.log('Facebook Authentication Successful:', data);

        // Redirect the user to the desired page
        navigateTo('/dashboard');
      } catch (error) {
        console.error('Facebook Authentication Error:', error);

        // Redirect the user to an error page or login page
        navigateTo('/login');
      }
    };

    handleFacebookResponse();
  }, [location.search, navigateTo]);

  return (
    <div>
      {/* You can render a loading spinner or other UI elements if needed */}
      <p>Processing Facebook authentication...</p>
    </div>
  );
};

export default FacebookCallback;
