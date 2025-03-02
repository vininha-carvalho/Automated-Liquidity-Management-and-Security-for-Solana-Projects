// PhantomConnect.tsx
import { useConnection, useWallet } from '@solana/wallet-adapter-react';

const PhantomButton = () => {
  const { connect, connected, publicKey } = useWallet();
  
  // Signing a transaction via Phantom
  const signAndSend = async (tx: Transaction) => {
    try {
      const { connection } = useConnection();
      const { signTransaction } = useWallet();
      
      tx.feePayer = publicKey!;
      tx.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
      
      const signed = await signTransaction(tx);
      const txid = await connection.sendRawTransaction(signed.serialize());
      
      return txid;
    } catch (err) {
      console.error("User rejected via Phantom");
      return null;
    }
  };

  return (
    <div>
      {!connected ? (
        <button onClick={() => connect()}>Connect Phantom</button>
      ) : (
        <div>Connected: {publicKey?.toBase58()}</div>
      )}
    </div>
  );
};
