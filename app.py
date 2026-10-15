import anthropic

client = anthropic.Anthropic()  # membaca ANTHROPIC_API_KEY dari environment

# 1. Fungsi nyata yang akan dijalankan oleh kode kita
def cek_harga(produk: str) -> str:
    harga = {"kopi": 25000, "teh": 15000, "roti": 12000}
    if produk.lower() in harga:
        return f"Harga {produk} adalah Rp{harga[produk.lower()]:,}"
    return f"Produk '{produk}' tidak ditemukan"

# 2. Definisi tool untuk LLM
tools = [
    {
        "name": "cek_harga",
        "description": "Mengecek harga sebuah produk di toko berdasarkan namanya.",
        "input_schema": {
            "type": "object",
            "properties": {
                "produk": {"type": "string", "description": "Nama produk, misalnya 'kopi'"}
            },
            "required": ["produk"],
        },
    }
]

messages = [{"role": "user", "content": "Berapa total harga 2 kopi dan 3 roti?"}]

# 3. Loop agent
while True:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        tools=tools,
        messages=messages,
    )

    # Jika LLM sudah selesai, tampilkan jawaban akhir
    if response.stop_reason != "tool_use":
        for block in response.content:
            if block.type == "text":
                print(block.text)
        break

    # Jika LLM meminta tool, jalankan lalu kirim hasilnya
    messages.append({"role": "assistant", "content": response.content})
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            hasil = cek_harga(**block.input)
            print(f"[Tool dipanggil] {block.name}({block.input}) -> {hasil}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": hasil,
            })
    messages.append({"role": "user", "content": tool_results})