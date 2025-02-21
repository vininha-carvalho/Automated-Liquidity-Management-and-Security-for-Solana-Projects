async function safeRequest(method, params) {
  try {
    const result = await connection[method](...params);
    return result;
  } catch (error) {
    console.error("RPC Error:", error);

    await reconnectToRpc();
    return safeRequest(method, params);
  }
}
