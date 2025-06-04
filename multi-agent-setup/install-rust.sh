#!/bin/bash

echo "Installing Rust and Cargo..."
echo "This script will download and run the official Rust installer."
echo ""

# Download and run the Rust installer
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Source the cargo environment
source "$HOME/.cargo/env"

# Verify installation
echo ""
echo "Verifying installation..."
rustc --version
cargo --version

echo ""
echo "Rust installation complete!"
echo "Note: You may need to restart your shell or run: source ~/.cargo/env"