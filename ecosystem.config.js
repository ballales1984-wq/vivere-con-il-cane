module.exports = {
  apps: [
    {
      name: "ngrok-vivere-con-il-cane",
      script: "python",
      args: "start_ngrok.py",
      cwd: "./",
      interpreter: "none",
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env: {
        NODE_ENV: "production",
        NGROK_AUTHTOKEN: "",  //://dashboard.ngrok.com/get-started/your-authtoken
        NGROK_DOMAIN: "tonita-deposable-manneristically.ngrok-free.dev"  // opzionale: il tuo dominio ngrok
      }
    }
  ]
};
