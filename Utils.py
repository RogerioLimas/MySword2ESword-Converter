import os


class Utils:
    @classmethod
    def create_output_directory(cls) -> str:
        """Cria o diretório de saída para os módulos"""
        
        output_directory = './output'

        temporary_directory = output_directory
        i = 2

        while os.path.exists(temporary_directory):
            temporary_directory = output_directory + str(i)
            i += 1

        os.makedirs(temporary_directory)
        return temporary_directory
