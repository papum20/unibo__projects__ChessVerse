import { useEffect } from "react";

function MyTimer({ paused, timer, expiryTimestamp }) {
  useEffect(() => {
    restart(timer);
    console.log("restart timer", timer);
  }, [timer]);

  useEffect(() => {
    if (paused) pause();
    else restart();
  }, [paused]);

  return (
    <div style={{ textAlign: "center" }}>
      <span style={{ marginLeft: "5px" }}>
        {minutes.toString().padStart(2, "0")}
      </span>
      :<span>{seconds.toString().padStart(2, "0")}</span>
    </div>
  );
}
export default MyTimer;
