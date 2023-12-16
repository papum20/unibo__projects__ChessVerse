import useWindowDimensions from "/code/app/src/components/useWindowDimensions.jsx";
import { test, expect } from "@jest/globals";

test("useWindowDimensions", () => {
  expect(useWindowDimensions()).toEqual({
    height: window.innerHeight,
    width: window.innerWidth,
  });
});
