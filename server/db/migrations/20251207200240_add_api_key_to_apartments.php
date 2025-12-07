<?php

declare(strict_types=1);

use Phinx\Migration\AbstractMigration;

final class AddApiKeyToApartments extends AbstractMigration
{
    public function change(): void
    {
        $this->table('apartments')
            ->addColumn('api_key', 'string', [
                'limit' => 64,
                'null' => true,
            ])
            ->addIndex(['api_key'], [
                'unique' => true,
                'name' => 'idx_apartments_api_key'
            ])
            ->save();
    }
}
