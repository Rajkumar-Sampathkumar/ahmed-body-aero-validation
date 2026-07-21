#! /usr/bin/env python3
import argparse
import math
import os
import sys

def calculate_first_cell_height(V, L, rho, mu, target_yplus):
    """Calculates the first cell height (in meters) based on flate-plate theory."""
    Re = (rho * V * L) / mu
    Cf = 0.0254 * math.pow(Re, -0.15)
    tau_w = 0.5 * Cf * rho * (V**2)
    u_star = math.sqrt(tau_w / rho)
    y_m = (target_yplus * mu) / (rho * u_star)

    return y_m, Re

def main ():
    parser = argparse.ArgumentParser(description="Automated Boundary Layer Mesh Configurator")

    # Physics inputs
    parser.add_argument("-v", "--velocity", type=float, required=True, help="Freestream velocity (m/s)")
    parser.add_argument("-l", "--length", type=float, required=True, help="Reference Length (m)")
    parser.add_argument("-rho", "--density", type=float, default=1.225, help="Air density (kg/m^3)")
    parser.add_argument("-mu", "--viscosity", type=float, default=1.789e-5, help="Dynamic viscosity (kg/(m*s))")
    parser.add_argument("-y", "--yplus", type=float, default=1.0, help="Target y+ value")

    # NEW: Mesh Control Inputs
    parser.add_argument("-nl", "--num_layers", type=int, default=10, help="Total number of prism layers")
    parser.add_argument("-er", "--expansion_ratio", type=float, default=1.2, help="Layer expansion ratio")

    # File paths
    parser.add_argument("-t", "--template", type=str, default="system/snappyHexMeshDict.template", help="Path to template file")
    parser.add_argument("-o", "--output", type=str, default="system/snappyHexMeshDict", help="Path to output file")

    args = parser.parse_args()

    # 1. Calculate the physics
    print(f"--- Mesh Configuration Execution ---")
    y_height_m, reynolds = calculate_first_cell_height(args.velocity, args.length, args.density, args.viscosity, args.yplus)

    print(f"Reynolds Number:    {reynolds:.2e}")
    print(f"Target y+:          {args.yplus}")
    print(f"First Layer (m):    {y_height_m:.6e}")
    print(f"Number of Layers:   {args.num_layers}")
    print(f"Expansion Ratio:    {args.expansion_ratio}")

    # 2. Inject into the dictionary template
    if not os.path.exists(args.template):
        print(f"Error: Template file '{args.template}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.template, 'r') as file:
            file_data = file.read()

        # Perform the text replacements
        new_data = file_data.replace("@FIRST_LAYER_THICKNESS@", f"{y_height_m:.6e}")
        new_data = new_data.replace("@NUM_LAYERS@", str(args.num_layers))
        new_data = new_data.replace("@EXPANSION_RATIO@", str(args.expansion_ratio))

        with open(args.output, 'w') as file:
            file.write(new_data)

        print(f"Success: Final snappyHexMeshDict generated at {args.output}")

    except Exception as e:
        print(f"Error processing files: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()    