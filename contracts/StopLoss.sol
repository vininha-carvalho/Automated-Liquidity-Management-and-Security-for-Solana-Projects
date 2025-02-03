// Dynamic stop loss with oracle
pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract SmartStopLoss {
    AggregatorV3Interface internal priceFeed;
    address public owner;
    uint256 public triggerPrice;
    bool public isActive;

    constructor(address _priceFeed) {
        priceFeed = AggregatorV3Interface(_priceFeed);
        owner = msg.sender;
    }

    function setStopLoss(uint256 _price) external {
        require(msg.sender == owner, "Only owner");
        triggerPrice = _price;
        isActive = true;
    }

    function checkCondition() public view returns (bool) {
        (, int256 price,,,) = priceFeed.latestRoundData();
        return isActive && uint256(price) <= triggerPrice;
    }

    function execute() external {
        require(checkCondition(), "Condition not met");
        // Integration with DEX for automatic sales
        isActive = false;
    }
}
