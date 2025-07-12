import uuid

class Inode:
    def __init__(self, name, is_dir, parent='~'):
        self.id = uuid.uuid4()
        self.name = name
        self.is_dir = is_dir
        self.size = 0
        self.children = {} if is_dir else None
        self.parent = parent
        self.content = "" if not is_dir else None

    def __repr__(self):
        return f"{'[DIR]' if self.is_dir else '[FILE]'} {self.name} (size: {self.size})"

NUMBER_INODES = 3

class FileSystem:
    def __init__(self):
        self.root = Inode("/", True)
        self.current = self.root
        self.path = [self.root]
        self.available_space = NUMBER_INODES
        self.list_allocated_inodes = [-1] * NUMBER_INODES
        print(f"available space: {self.available_space}")

    def space_can_use(self):
        print(f"available space: {self.available_space}")
        for index, inode_id in enumerate(self.list_allocated_inodes):
            print(f"index {index}: id {inode_id}")

    def _get_path_str(self): # Mostra o caminho atual no path
        return "/" + "/".join(node.name for node in self.path[1:])

    def mkdir(self, name): # Cria um novo diretório
        if name in self.current.children:
            print("Directory already exists.")
        elif self.available_space > 0: #Se tiver espaço disponível, vai passar desse if
            for i, value in enumerate(self.list_allocated_inodes):
                if value == -1:
                    new_inode = Inode(name, True, self.current)
                    self.list_allocated_inodes[i] = new_inode.id
                    self.current.children[name] = new_inode
                    self.available_space -= 1
                    break
        else: 
            print("No free space available.")
        
    def touch(self, name): # Cria um novo arquivo
        if name in self.current.children:
            print("File already exists.")
        elif self.available_space > 0: #Se tiver espaço disponível, vai passar desse if
            for i, value in enumerate(self.list_allocated_inodes):
                if value == -1:
                    new_inode = Inode(name, False, self.current)
                    self.list_allocated_inodes[i] = new_inode.id
                    self.current.children[name] = new_inode
                    self.available_space -= 1
                    break
        else: 
            print("No free space available.")
    
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
    
    # Função acessório para mv
    def resolve_path(self, path):
        parts = path.strip("/").split("/")
        node = self.root if path.startswith("/") else self.current

        for part in parts:
            if part == '' or part == '.':
                continue
            elif part == '..':
                if node.parent != '~':
                    node = node.parent
            elif part in node.children and node.children[part].is_dir:
                node = node.children[part]
            else:
                return None
        return node
    def mv(self, src, dest_path):
        if src not in self.current.children:
            print("Source file not found.")
            return

        dest_dir = self.resolve_path(dest_path)
        if not dest_dir or not dest_dir.is_dir:
            print("Destination directory not found.")
            return

        inode = self.current.children.pop(src)
        dest_dir.children[src] = inode
        inode.parent = dest_dir


    def write(self, name, data): # Escreve dentro de um arquivo
        if name in self.current.children and not self.current.children[name].is_dir:
            inode = self.current.children[name]
            inode.content += data
            inode.size = len(inode.content)
        else:
            print("File not found.")

    def read(self, name): # Le um arquivo
        if name in self.current.children and not self.current.children[name].is_dir:
            print(self.current.children[name].content)
        else:
            print("File not found.")

    def rm(self, name): # Remove arquivo ou diretório
        # Deve haver recursividade, quando o diretorio tiver arquivos dentro dele
        if name in self.current.children:
            def _recursive_delete(inode):
                if inode.is_dir:
                    for child in list(inode.children.values()):
                            _recursive_delete(child)
                    inode.children.clear()
                    inode.content = ""
                    inode.size = 0
                    self.available_space += 1
                    for i, value in enumerate(self.list_allocated_inodes):
                        if value == inode.id:
                            self.list_allocated_inodes[i] = -1
                    inode.id = -1

            inode = self.current.children[name]
            _recursive_delete(inode)
            del self.current.children[name]
        else:
            print("File or directory not found.")

    def inode(self, name): # Comando para verificar o inode do arquivo ou diretório
        
        if len(name) == 1 and name == ".":
            print(f"Informações do INode: \nId\t\t{self.current.id}\nName\t\t{name}\nIs_dir\t\t{self.current.is_dir}\nParent\t\t{self.current.parent}\nContent\t\t{self.current.content}\n")
        if name in self.current.children:
            print(f"Informações do INode: \nId\t\t{self.current.children[name].id}\nName\t\t{name}\nIs_dir\t\t{self.current.children[name].is_dir}\nParent\t\t{self.current.children[name].parent}\nContent\t\t{self.current.children[name].content}\n")
        else:
            print("Directory not found.")

    def pwd(self):
        print(self._get_path_str())

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
                case 'space':
                    self.space_can_use()
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
                case 'inode':
                    if args:
                        self.inode(args[0])
                case 'pwd':
                    self.pwd()
                case _:
                    print("Invalid command or arguments")

if __name__ == "__main__":
    fs = FileSystem()
    fs.run()