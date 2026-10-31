## idoly-asset-curator

Asset backend for [info-pride](https://github.com/outloudvi/info-pride).

It is deployed to [Vercel](https://vercel.com/) (over [`vercel.json`](./vercel.json)) and [Azure App Service](https://azure.microsoft.com/en-us/services/app-service/#faq) (over [`app.py`](./app.py)) at the same time.

### Why not using Vercel only?

I failed to add `ffmpeg` to my bundle for Vercel.

### Why not using Azure App Service only?

💸

## Tests

```sh
uv sync --frozen --python 3.12
uv run python -m unittest discover -s tests -v
```

Tests mock B2 and upstream asset processing; no live storage credentials are
needed.

## License

AGPLv3
