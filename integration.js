const { Connection } = require("@solana/web3.js");
const customRpcUrl = "https://lb.drpc.org/ogrpc?network=solana&dkey=Arc_JqtwaUlmmje2rvgtJWyamxyDxxAR77DXIlZWwHzRp:8899"; // https://lb.drpc.org/ogrpc?network=solana&dkey=Arc_JqtwaUlmmje2rvgtJWyamxyDxxAR77DXIlZWwHzR
const connection = new Connection(customRpcUrl, "confirmed");
