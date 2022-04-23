// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

// Ä~©ÓERC721URIStorage
contract LAN_NFT is ERC721URIStorage {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;
    event CreatedNFT(uint256 indexed tokenId, string tokenURI);
    
    constructor() ERC721("LAN_NFT", "LAN_NFT"){}
    function mint (string memory _tokenURI) public returns (uint256 tokenId) {
        tokenId = _tokenIds.current();
        _safeMint(msg.sender, tokenId);
        _setTokenURI(tokenId, _tokenURI);
        emit CreatedNFT(tokenId, _tokenURI);
        _tokenIds.increment();
    }

    function burn(uint256 tokenId) public virtual {
        // solhint-disable-next-line max-line-length
        require(_isApprovedOrOwner(_msgSender(), tokenId), "ERC721Burnable: caller is not owner nor approved");
        _burn(tokenId);
    }
}