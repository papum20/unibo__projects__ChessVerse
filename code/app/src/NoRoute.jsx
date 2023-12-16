import { Button } from "@mui/material";
import { Link } from "react-router-dom";

function NoRoute() {
  return (
    <div data-testid="noRoutePage">
      <div style={{ marginTop: "30%", marginLeft: "40%" }}>
        <span data-testid="textComponent">torna alla pagina di </span>
        <Button as={Link} to="/" variant="contained" data-testid="goBack">
          start
        </Button>
      </div>
    </div>
  );
}
export default NoRoute;
