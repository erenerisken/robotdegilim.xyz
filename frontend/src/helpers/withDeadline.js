// Rejects if the promise has not settled in time. A request that never settles
// would otherwise leave the caller waiting forever.
export function withDeadline(promise, ms, message = "Timed out") {
  let timer;
  const deadline = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(message)), ms);
  });

  return Promise.race([promise, deadline]).finally(() => clearTimeout(timer));
}
