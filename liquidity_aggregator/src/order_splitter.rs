// Algorithm of large orders splitting to minimize slippage
use crate::exchange_connector::Orderbook;

pub fn smart_order_split(order_size: f64, orderbook: &Orderbook) -> Vec<f64> {
    let mut remaining = order_size;
    let mut chunks = Vec::new();
    
    // Calculate the optimum chunk size based on the depth of the cup
    for level in &orderbook.bids {
        let available = level.amount.min(remaining);
        if available > 0.0 {
            chunks.push(available);
            remaining -= available;
        }
        if remaining <= 0.0 { break; }
    }
    
    // Add the remaining volume as a market order with a warning message
    if remaining > 0.0 {
        chunks.push(remaining);
        log::warn!("Order partially filled! Remaining: {}", remaining);
    }
    
    chunks
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_order_split() {
        let orderbook = Orderbook {
            bids: vec![
                Level { price: 100.0, amount: 0.5 },
                Level { price: 99.5, amount: 1.2 },
            ]
        };
        
        assert_eq!(
            smart_order_split(1.0, &orderbook),
            vec![0.5, 0.5]
        );
    }
}
