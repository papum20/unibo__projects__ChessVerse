/*
 * utilities for managing and performing operations on paths (and urls).
 */

export function joinPaths(...paths) {
  return paths
    .map((path, index) => {
      if (index === 0) {
        return path.replace(/\/+$/, ""); // Trim trailing slashes from the first segment
      } else {
        return path.replace(/^\/+/, ""); // Trim leading slashes from subsequent segments
      }
    })
    .join("/");
}
