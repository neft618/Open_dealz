import React from 'react';

const EscrowStatus = ({ contract }) => (
  <div className="bg-gray-50 p-4 rounded">
    <h3 className="text-lg font-medium mb-2">Escrow Status</h3>
    <p>Total Amount: ${contract.total_amount}</p>
    <p>Platform Fee: ${contract.platform_fee}</p>
    <p>Executor Payout: ${contract.total_amount - contract.platform_fee}</p>
    <div className="mt-4">
      <h4 className="font-medium">Transactions</h4>
      {contract.escrow_transactions?.map((tx) => (
        <div key={tx.id} className="text-sm">
          {tx.type}: ${tx.amount} - {tx.status}
        </div>
      ))}
    </div>
  </div>
);

export default EscrowStatus;