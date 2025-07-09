import uuid

class Inode:
    def __init__(self, name, is_dir):
        self.id = uuid.uuid4()
        self.name = name
        self.is_dir = is_dir
        self.size = 0
        self.data_blocks = []
        self.children = {} if is_dir else None
        self.parent = None
        self.content = "" if not is_dir else None
        self.blocks = []

    def __repr__(self):
        return f"{'[DIR]' if self.is_dir else '[FILE]'} {self.name} (size: {self.size})"

class FileSystem:
    def __init__(self):
        self.root = Inode("/", True)
        self.current = self.root
        self.path = [self.root]

    def _get_path_str(self): # Mostra o caminho atual no path
        return "/" + "/".join(node.name for node in self.path[1:])

    def mkdir(self, name): # Cria um novo diretório
        if name in self.current.children:
            print("Directory already exists.")
        else: 
            self.current.children[name] = Inode(name, True)

    def touch(self, name): # Cria um novo arquivo
        if name in self.current.children:
            print("File already exists.")
        else:
            self.current.children[name] = Inode(name, False)
    
    def ls(self): # Lista os filhos do diretório atual
        for name in self.current.children:
            inode = self.current.children[name]
            print(f"{name}/" if inode.is_dir else name)

    def cd(self, name): # Navega entre os repositórios
        if name == "..":
            if len(self.path) > 1:
                self.path.pop()
                self.current = self.path[-1]
        elif name == ".":
            pass
        elif name in self.current.children and self.current.children[name].is_dir:
            self.current = self.current.children[name]
            self.path.append(self.current)
        else:
            print("Directory not found.")

    def mv(self, src, dest): # Move arquivos/diretórios
        if src not in self.current.children:
            print("Source file not found.")
            return
        if dest not in self.current.children or not self.current.children[dest].is_dir:
            print("Destination directory not found.")
            return
        inode = self.current.children.pop(src)
        self.current.children[dest].children[src] = inode

    def write(self, name, data): # Escreve dentro de um arquivo
        if name in self.current.children and not self.current.children[name].is_dir:
            inode = self.current.children[name]
            inode.content += data
            inode.size = len(inode.content)
            inode.blocks = list(range(0, inode.size, 4))
        else:
            print("File not found.")

    def read(self, name): # Le um arquivo
        if name in self.current.children and not self.current.children[name].is_dir:
            print(self.current.children[name].content)
        else:
            print("File not found.")

    def rm(self, name): # Remove arquivo ou diretório
        if name in self.current.children:
            del self.current.children[name]
        else:
            print("File or directory not found.")

    def run(self):
        while True:
            cmd = input(f"{self._get_path_str()}$ ").strip().split()
            if not cmd:
                continue
            command = cmd[0]
            args = cmd[1:]

            match command:
                case 'exit': # Finaliza a execução
                    break
                case 'cd':
                    if args:
                        self.cd(args[0])
                case 'mkdir':
                    if args:
                        self.mkdir(args[0])
                case 'touch':
                    if args:
                        self.touch(args[0])
                case 'mv':
                    if len(args) == 2:
                        self.mv(args[0], args[1])
                case 'write':
                    if len(args) >= 2:
                        self.write(args[0], " ".join(args[1:]))
                case 'read':
                    if args:
                        self.read(args[0])
                case 'ls':
                    self.ls()
                case 'rm':
                    if args:
                        self.rm(args[0])
                case _:
                    print("Invalid command or arguments")

if __name__ == "__main__":
    fs = FileSystem()
    fs.run()
