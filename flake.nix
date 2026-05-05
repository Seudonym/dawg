{
  description = "DAWG flake";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };
  outputs =
    { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
        config = {
          allowUnfree = true;
          cudaSupport = true;
        };
      };
      cudaPackages = pkgs.cudaPackages;
    in
    {
      devShells.x86_64-linux.default = pkgs.mkShell {
        packages = with pkgs; [
          uv
          basedpyright
          black

          ffmpeg
          portaudio

          gcc
          stdenv.cc.cc.lib

          cudaPackages.cudatoolkit
          cudaPackages.cudnn
        ];

        shellHook = ''
          export CUDA_HOME=${cudaPackages.cudatoolkit}
          export CUDA_PATH=${cudaPackages.cudatoolkit}
          export PATH=${cudaPackages.cudatoolkit}/bin:$PATH
          export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc
            cudaPackages.cudatoolkit
            cudaPackages.cudnn
          ]}:/run/opengl-driver/lib:/run/opengl-driver-32/lib:$LD_LIBRARY_PATH
          export LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
            cudaPackages.cudatoolkit
            cudaPackages.cudnn
          ]}:$LIBRARY_PATH
          export CPATH=${cudaPackages.cudatoolkit}/include:$CPATH
        '';
      };

    };
}
