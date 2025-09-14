export default {
    "^/(app|api|assets|files|private)": {
      target: "https://testapp.speedym.com",
    //   changeOrigin: true,
    //   secure: false,
    //   ws: true,
      rewrite: (path) => path,
    },
  };