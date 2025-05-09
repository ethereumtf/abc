// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract ABCToken is ERC20, Ownable {
    uint256 public constant TOTAL_SUPPLY = 1_000_000_000 * 10**18;

    address public daoPool;
    address public contributorPool;

    constructor(address _daoPool, address _contributorPool) ERC20("Artificial Builders", "ABC") {
        require(_daoPool != address(0), "Invalid DAO pool address");
        require(_contributorPool != address(0), "Invalid contributor pool address");

        daoPool = _daoPool;
        contributorPool = _contributorPool;

        _mint(daoPool, TOTAL_SUPPLY / 2);
        _mint(contributorPool, TOTAL_SUPPLY / 2);
    }

    function updateDaoPool(address _newDaoPool) external onlyOwner {
        require(_newDaoPool != address(0), "Invalid DAO pool address");
        daoPool = _newDaoPool;
    }

    function updateContributorPool(address _newContributorPool) external onlyOwner {
        require(_newContributorPool != address(0), "Invalid contributor pool address");
        contributorPool = _newContributorPool;
    }

    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
}
